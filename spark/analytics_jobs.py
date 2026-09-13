"""
Chương trình Phân Tích Dữ Liệu Lớn & Thống Kê Nhu Cầu Tuyển Dụng CNTT
(Big Data Analytics & Aggregation Engine)
Thực thi toàn bộ 5 bài toán phân tích trọng tâm theo Chương 3.3 Đề Cương:
1. Top kỹ năng phổ biến nhất thị trường (Programming Languages, Frameworks, Cloud, Data)
2. Top vị trí tuyển dụng có nhu cầu cao nhất (Backend, Frontend, Fullstack, AI, Data...)
3. Phân bố địa lý việc làm CNTT theo thành phố (Hà Nội, TP.HCM, Đà Nẵng, Remote...)
4. Mức lương trung bình theo vị trí và số năm kinh nghiệm
5. Mối quan hệ tương quan giữa Kỹ năng và Thu nhập (Skills vs Salary Insights)
Xuất kết quả thành các bảng Data Marts (CSV / Parquet) cho Power BI Desktop.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Cấu hình UTF-8 cho console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from hdfs.hdfs_manager import HDFSManager

class BigDataAnalytics:
    def __init__(self, cleaned_df):
        self.df = cleaned_df
        self.hdfs_manager = HDFSManager()
        self.marts_dir = Path(self.hdfs_manager.marts_dir)
        self.marts_dir.mkdir(parents=True, exist_ok=True)

    def run_all_analyses(self):
        """Thực thi toàn bộ các phép biến đổi và tổng hợp số liệu"""
        print("\n" + "=" * 60)
        print("BẮT ĐẦU THỰC THI 5 BÀI TOÁN PHÂN TÍCH BIG DATA (SPARK SQL / AGGREGATION)")
        print("=" * 60)

        results = {}
        results["overview_kpi"] = self.compute_kpis()
        results["top_skills"] = self.analyze_top_skills(top_n=20)
        results["top_roles"] = self.analyze_top_roles()
        results["location_distribution"] = self.analyze_location_distribution()
        results["salary_by_role_exp"] = self.analyze_salary_by_role_and_experience()
        results["skills_salary"] = self.analyze_skills_vs_salary(top_n=15)

        self.export_data_marts(results)
        return results

    def compute_kpis(self):
        """Chỉ số KPI tổng quan toàn thị trường"""
        total_jobs = len(self.df)
        total_companies = self.df["company_name"].nunique()
        salary_available = self.df["salary_avg"].dropna()
        avg_salary = round(salary_available.mean(), 1) if not salary_available.empty else 0.0
        median_salary = round(salary_available.median(), 1) if not salary_available.empty else 0.0

        kpi_df = pd.DataFrame([{
            "total_jobs": total_jobs,
            "total_companies": total_companies,
            "average_salary_million_vnd": avg_salary,
            "median_salary_million_vnd": median_salary
        }])
        print(f"[KPIs] Tổng tin tuyển dụng: {total_jobs} | Số công ty: {total_companies} | Lương TB: {avg_salary} triệu VNĐ")
        return kpi_df

    def analyze_top_skills(self, top_n=20):
        """Bài toán 1: Top kỹ năng công nghệ phổ biến nhất"""
        all_skills = []
        for skills_list in self.df["skills"]:
            if isinstance(skills_list, list):
                all_skills.extend(skills_list)
        
        skill_series = pd.Series(all_skills)
        skill_counts = skill_series.value_counts().reset_index()
        skill_counts.columns = ["skill_name", "job_count"]
        skill_counts["percentage"] = round((skill_counts["job_count"] / len(self.df)) * 100, 2)
        top_df = skill_counts.head(top_n)

        print(f"\n[Phân tích 1] Top 5 Kỹ năng được săn đón nhất:")
        for idx, row in top_df.head(5).iterrows():
            print(f"  - {row['skill_name']}: {row['job_count']} tin ({row['percentage']}%)")
        return top_df

    def analyze_top_roles(self):
        """Bài toán 2: Top vị trí / vai trò tuyển dụng nhiều nhất"""
        role_counts = self.df["role_category"].value_counts().reset_index()
        role_counts.columns = ["role_category", "job_count"]
        role_counts["percentage"] = round((role_counts["job_count"] / len(self.df)) * 100, 2)

        print(f"\n[Phân tích 2] Phân bố Vị trí tuyển dụng:")
        for idx, row in role_counts.iterrows():
            print(f"  - {row['role_category']}: {row['job_count']} tin ({row['percentage']}%)")
        return role_counts

    def analyze_location_distribution(self):
        """Bài toán 3: Phân bố việc làm IT theo khu vực địa lý"""
        loc_counts = self.df["location_standard"].value_counts().reset_index()
        loc_counts.columns = ["location", "job_count"]
        loc_counts["percentage"] = round((loc_counts["job_count"] / len(self.df)) * 100, 2)

        print(f"\n[Phân tích 3] Phân bố Việc làm theo Thành phố:")
        for idx, row in loc_counts.iterrows():
            print(f"  - {row['location']}: {row['job_count']} tin ({row['percentage']}%)")
        return loc_counts

    def analyze_salary_by_role_and_experience(self):
        """Bài toán 4: Mức lương trung bình theo Vị trí & Cấp bậc kinh nghiệm"""
        valid_salary = self.df.dropna(subset=["salary_avg"])
        if valid_salary.empty:
            return pd.DataFrame()

        salary_agg = valid_salary.groupby(["role_category", "seniority_level"]).agg(
            job_count=("job_id", "count"),
            salary_min_avg=("salary_min", "mean"),
            salary_max_avg=("salary_max", "mean"),
            salary_mean=("salary_avg", "mean"),
            salary_median=("salary_avg", "median")
        ).reset_index()

        salary_agg["salary_min_avg"] = salary_agg["salary_min_avg"].round(1)
        salary_agg["salary_max_avg"] = salary_agg["salary_max_avg"].round(1)
        salary_agg["salary_mean"] = salary_agg["salary_mean"].round(1)
        salary_agg["salary_median"] = salary_agg["salary_median"].round(1)

        print(f"\n[Phân tích 4] Mức lương trung bình theo Vai trò & Kinh nghiệm (Trích xuất 5 nhóm):")
        for idx, row in salary_agg.head(5).iterrows():
            print(f"  - {row['role_category']} ({row['seniority_level']}): Lương TB {row['salary_mean']} triệu (Khoảng {row['salary_min_avg']} - {row['salary_max_avg']} tr)")
        return salary_agg

    def analyze_skills_vs_salary(self, top_n=15):
        """Bài toán 5: Mối quan hệ giữa Kỹ năng công nghệ và Thu nhập trung bình"""
        valid_salary = self.df.dropna(subset=["salary_avg"])
        if valid_salary.empty:
            return pd.DataFrame()

        skill_salary_data = []
        for idx, row in valid_salary.iterrows():
            sal = row["salary_avg"]
            for skill in row["skills"]:
                skill_salary_data.append({"skill": skill, "salary": sal})

        skill_sal_df = pd.DataFrame(skill_salary_data)
        if skill_sal_df.empty:
            return pd.DataFrame()

        skill_sal_agg = skill_sal_df.groupby("skill").agg(
            sample_count=("salary", "count"),
            salary_avg=("salary", "mean"),
            salary_median=("salary", "median")
        ).reset_index()

        # Lọc các kỹ năng có ít nhất 3 mẫu tin tuyển dụng để đảm bảo độ tin cậy
        filtered = skill_sal_agg[skill_sal_agg["sample_count"] >= 3].copy()
        filtered["salary_avg"] = filtered["salary_avg"].round(1)
        filtered["salary_median"] = filtered["salary_median"].round(1)
        top_paid_skills = filtered.sort_values(by="salary_avg", ascending=False).head(top_n)

        print(f"\n[Phân tích 5] Top Kỹ năng được định giá thu nhập cao nhất:")
        for idx, row in top_paid_skills.head(5).iterrows():
            print(f"  - {row['skill']}: Thu nhập TB {row['salary_avg']} triệu ({row['sample_count']} mẫu)")
        return top_paid_skills

    def export_data_marts(self, results):
        """Xuất các bảng kết quả Data Marts phục vụ Power BI Desktop & Dashboard"""
        print("\n" + "-" * 60)
        print("[Data Marts Export] Đang ghi các bảng tổng hợp vào thư mục data/marts/...")
        for name, data in results.items():
            if isinstance(data, pd.DataFrame):
                csv_path = self.marts_dir / f"mart_{name}.csv"
                json_path = self.marts_dir / f"mart_{name}.json"
                data.to_csv(csv_path, index=False, encoding="utf-8-sig")
                data.to_json(json_path, orient="records", force_ascii=False, indent=2)
                print(f"  -> Đã tạo Data Mart: {csv_path.name}")
        print("[Data Marts Export] Hoàn thành xuất kho dữ liệu tổng hợp cho Power BI!")
