"""
Apache NiFi Orchestrator & Pipeline Trigger
Mô phỏng và điều phối luồng dữ liệu NiFi theo Đề cương (Chương 3.1):
1. ExecuteProcess: Kích hoạt kịch bản crawler Python theo chu kỳ (Cron-job).
2. Packaging FlowFile: Đóng gói các bản tin tuyển dụng thành FlowFile JSON.
3. PutHDFS: Đưa dữ liệu thô vào Hadoop HDFS Raw Zone.
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Cấu hình UTF-8 cho console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Thêm thư mục gốc vào path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from hdfs.hdfs_manager import HDFSManager

def run_nifi_ingestion_flow(pages=3):
    """
    Thực thi luồng Ingestion tương đương đồ thị NiFi Dataflow:
    Crawler Script -> FlowFile Producer -> HDFS Put Processor
    """
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [NiFi Flow] Bắt đầu kích hoạt luồng Data Ingestion...")
    print("=" * 60)

    # 1. Kích hoạt Python Crawler (ExecuteProcess Processor)
    crawler_script = ROOT_DIR / "crawler" / "run_crawler.py"
    print(f"[NiFi Processor: ExecuteProcess] Đang gọi {crawler_script} (pages={pages})...")
    
    cmd = [sys.executable, str(crawler_script), "--pages", str(pages)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    
    if result.returncode != 0:
        print(f"[NiFi Processor: ExecuteProcess] LỖI: {result.stderr}")
        return False
    
    print(result.stdout)
    
    # 2. Định tuyến FlowFile và đẩy vào HDFS (PutHDFS Processor)
    print("[NiFi Processor: PutHDFS] Đang chuyển giao FlowFile vào Hadoop HDFS Raw Zone...")
    hdfs_manager = HDFSManager()
    latest_files = hdfs_manager.get_latest_raw_files()
    
    if not latest_files:
        print("[NiFi Processor: PutHDFS] Cảnh báo: Không tìm thấy file dữ liệu thô nào.")
        return False
    
    latest_file = max(latest_files, key=os.path.getctime)
    hdfs_dest = hdfs_manager.put_raw_data(latest_file)
    
    print(f"[NiFi Processor: PutHDFS] Thành công đưa FlowFile vào HDFS: {hdfs_dest}")
    print(f"[NiFi Status] Luồng Ingestion hoàn thành xuất sắc!")
    return True

if __name__ == "__main__":
    pages = 2
    if len(sys.argv) > 1:
        try:
            pages = int(sys.argv[1])
        except ValueError:
            pass
    run_nifi_ingestion_flow(pages=pages)
