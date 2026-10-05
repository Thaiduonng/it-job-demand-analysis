"""
HDFS & Data Lake Storage Manager
Hỗ trợ Dual-mode:
1. Cluster Mode: Giao tiếp trực tiếp với Hadoop HDFS (thông qua WebHDFS / pyarrow hdfs).
2. Standalone / Local Lake Mode: Lưu trữ phân vùng trên local filesystem theo cấu trúc
   chuẩn HDFS (/data/raw/zone/ và /data/processed/zone/) giúp chạy trơn tru cả khi không bật Docker.
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

# Cấu hình encoding UTF-8 cho console Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

class HDFSManager:
    def __init__(self, base_data_dir=None, hdfs_host="localhost", hdfs_port=9870):
        if base_data_dir is None:
            project_root = Path(__file__).resolve().parent.parent
            base_data_dir = project_root / "data"
        
        self.base_dir = Path(base_data_dir)
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.marts_dir = self.base_dir / "marts"
        
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.marts_dir.mkdir(parents=True, exist_ok=True)
        
        self.hdfs_host = hdfs_host
        self.hdfs_port = hdfs_port
        self.is_hdfs_available = self._check_hdfs_connection()

    def _check_hdfs_connection(self):
        """Kiểm tra xem cụm Hadoop HDFS (WebHDFS hoặc RPC) có đang hoạt động không"""
        try:
            import urllib.request
            url = f"http://{self.hdfs_host}:{self.hdfs_port}/webhdfs/v1/?op=LISTSTATUS"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def put_raw_data(self, file_path, partition_date=None):
        """
        Đưa dữ liệu thô (JSON/JSONL) vào Raw Zone (HDFS hoặc Local Data Lake).
        Phân vùng theo ngày: /data/raw/jobs/year=YYYY/month=MM/day=DD/
        """
        if partition_date is None:
            now = datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")
        else:
            year, month, day = partition_date.split("-")

        dest_partition_dir = self.raw_dir / f"year={year}" / f"month={month}" / f"day={day}"
        dest_partition_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = Path(file_path).name
        dest_file_path = dest_partition_dir / file_name
        
        # Sao chép vào partition
        shutil.copy2(file_path, dest_file_path)
        print(f"[HDFSManager] Đã lưu tệp vào Raw Zone: {dest_file_path}")

        # Nếu HDFS Cluster đang chạy, tải tiếp lên HDFS WebHDFS
        if self.is_hdfs_available:
            self._upload_to_webhdfs(dest_file_path, f"/data/raw/jobs/year={year}/month={month}/day={day}/{file_name}")

        return str(dest_file_path)

    def _upload_to_webhdfs(self, local_path, hdfs_path):
        """Tải tệp lên HDFS thông qua WebHDFS REST API"""
        try:
            import requests
            import re
            create_url = f"http://{self.hdfs_host}:{self.hdfs_port}/webhdfs/v1{hdfs_path}?op=CREATE&overwrite=true"
            r = requests.put(create_url, allow_redirects=False, timeout=5)
            if r.status_code == 307:
                redirect_url = r.headers.get("Location")
                if redirect_url:
                    # Thay thế hostname/container ID của DataNode bằng localhost
                    dest_url = re.sub(r"http://[^:]+:9864", f"http://{self.hdfs_host}:9864", redirect_url)
                    with open(local_path, "rb") as f:
                        final_r = requests.put(dest_url, data=f, timeout=15)
                        if final_r.status_code in (200, 201):
                            print(f"[HDFS Cluster] Tải thành công lên WebHDFS: {hdfs_path} (Status {final_r.status_code})")
        except Exception as e:
            print(f"[HDFS Cluster] Không thể upload WebHDFS: {e}. Đã lưu an toàn ở Local Lake.")

    def get_latest_raw_files(self):
        """Lấy danh sách tất cả các file thô trong Raw Zone"""
        raw_files = list(self.raw_dir.glob("**/*.json")) + list(self.raw_dir.glob("**/*.jsonl"))
        return [str(f) for f in raw_files]

    def get_processed_path(self, table_name="jobs_cleaned"):
        """Đường dẫn lưu trữ dữ liệu sau khi Spark làm sạch (Parquet)"""
        path = self.processed_dir / table_name
        return str(path)

    def get_marts_path(self, mart_name):
        """Đường dẫn lưu trữ Data Marts cho Power BI"""
        path = self.marts_dir / mart_name
        return str(path)


if __name__ == "__main__":
    manager = HDFSManager()
    print("Trạng thái Hadoop HDFS Cluster:", "ONLINE" if manager.is_hdfs_available else "OFFLINE (Sử dụng Local Data Lake)")
    print("Thư mục Raw Zone:", manager.raw_dir)
    print("Thư mục Processed Zone:", manager.processed_dir)
    print("Thư mục Data Marts:", manager.marts_dir)
