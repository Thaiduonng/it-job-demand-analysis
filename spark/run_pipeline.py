"""
Pipeline Điều Phối Xử Lý & Phân Tích Dữ Liệu Lớn (Big Data Processing Pipeline)
Thực thi trọn vẹn: Raw Zone -> Data Cleaning & Feature Extraction -> Processed Zone (Parquet) -> Data Marts
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Cấu hình UTF-8 cho console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from hdfs.hdfs_manager import HDFSManager
from spark.clean_data import parse_salary, parse_location, parse_experience
from spark.skill_extractor import extract_skills_from_text
from spark.role_classifier import classify_job_role
from spark.analytics_jobs import BigDataAnalytics

def run_spark_pipeline():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] KHỞI ĐỘNG PIPELINE XỬ LÝ DỮ LIỆU LỚN SPARK")
    print("=" * 60)

    hdfs_manager = HDFSManager()
    raw_files = hdfs_manager.get_latest_raw_files()

    if not raw_files:
        print("[Lỗi] Chưa có dữ liệu thô trong Raw Zone. Hãy chạy crawler trước!")
        return False

    print(f"[HDFS Raw Zone] Đã tìm thấy {len(raw_files)} tệp dữ liệu thô. Đang nạp dữ liệu...")

    # 1. Đọc toàn bộ dữ liệu thô vào bảng
    raw_records = []
    for fpath in raw_files:
        try:
            if fpath.endswith(".json"):
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        raw_records.extend(data)
                    elif isinstance(data, dict):
                        raw_records.append(data)
            elif fpath.endswith(".jsonl"):
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            raw_records.append(json.loads(line))
        except Exception as e:
            print(f"[Cảnh báo] Bỏ qua file lỗi {fpath}: {e}")

    print(f"[Raw Load] Tổng số bản ghi thô nạp vào: {len(raw_records)}")
    if not raw_records:
        return False

    df_raw = pd.DataFrame(raw_records)

    # 2. Tiền xử lý & Khử trùng lặp (Deduplication)
    initial_count = len(df_raw)
    df_clean = df_raw.drop_duplicates(subset=["job_id"]).copy()
    if "company_name" in df_clean.columns and "job_title" in df_clean.columns:
        df_clean = df_clean.drop_duplicates(subset=["job_title", "company_name"]).copy()
    
    print(f"[Spark Deduplication] Loại bỏ {initial_count - len(df_clean)} bản ghi trùng lặp. Còn lại {len(df_clean)} bản ghi độc nhất.")

    # 3. Trích xuất đặc trưng & Chuẩn hóa (Transformation & Feature Extraction)
    processed_records = []
    for idx, row in df_clean.iterrows():
        title = str(row.get("job_title", "")).strip()
        company = str(row.get("company_name", "")).strip()
        loc_raw = str(row.get("location", ""))
        sal_raw = str(row.get("salary_raw", ""))
        exp_raw = str(row.get("experience_req", ""))
        desc_raw = str(row.get("job_description", ""))
        skills_existing = row.get("skills_raw", [])

        # Chuẩn hóa địa điểm
        loc_standard = parse_location(loc_raw)

        # Chuẩn hóa mức lương (triệu VND)
        sal_min, sal_max, sal_avg = parse_salary(sal_raw)

        # Chuẩn hóa số năm kinh nghiệm & cấp bậc
        exp_min, exp_max, seniority = parse_experience(exp_raw)

        # Trích xuất kỹ năng bằng Regex biên từ
        combined_text = f"{title} {desc_raw}"
        skills = extract_skills_from_text(combined_text, existing_skills=skills_existing)

        # Phân loại vai trò ngành IT
        role_category = classify_job_role(title, desc_raw)

        processed_records.append({
            "job_id": row.get("job_id"),
            "job_title": title,
            "company_name": company,
            "location_raw": loc_raw,
            "location_standard": loc_standard,
            "salary_raw": sal_raw,
            "salary_min": sal_min,
            "salary_max": sal_max,
            "salary_avg": sal_avg,
            "experience_raw": exp_raw,
            "exp_min_years": exp_min,
            "exp_max_years": exp_max,
            "seniority_level": seniority,
            "skills": skills,
            "skills_count": len(skills),
            "skills_str": ", ".join(skills),
            "role_category": role_category,
            "date_posted": row.get("date_posted", datetime.now().strftime("%Y-%m-%d")),
            "job_url": row.get("job_url", ""),
            "source": row.get("source", "WebCrawler")
        })

    df_processed = pd.DataFrame(processed_records)

    # 4. Lưu dữ liệu đã làm sạch vào HDFS Processed Zone (Parquet & CSV)
    processed_dir = Path(hdfs_manager.processed_dir)
    parquet_path = processed_dir / "jobs_cleaned.parquet"
    csv_path = processed_dir / "jobs_cleaned.csv"

    # Lưu định dạng Parquet (chuẩn Big Data)
    df_processed.to_parquet(parquet_path, index=False, engine="pyarrow")
    # Lưu CSV UTF-8 BOM để mở tốt trên Excel/Power BI
    df_processed.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"[HDFS Processed Zone] Đã xuất Parquet Lake: {parquet_path}")
    print(f"[HDFS Processed Zone] Đã xuất CSV làm sạch:  {csv_path}")

    # 5. Thực thi 5 bài toán phân tích & xuất Data Marts
    analytics = BigDataAnalytics(df_processed)
    analytics.run_all_analyses()

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PIPELINE XỬ LÝ & PHÂN TÍCH HOÀN THÀNH THÀNH CÔNG!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    run_spark_pipeline()
