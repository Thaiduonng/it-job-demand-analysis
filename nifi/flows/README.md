# Hướng Dẫn Cấu Hình Apache NiFi Dataflow

Hệ thống cung cấp quy trình Ingestion tự động hóa thông qua Apache NiFi theo thiết kế tại **Chương 3.1 của Đề cương đồ án**.

## 1. Truy cập Web UI của Apache NiFi
Khi cụm Docker Compose khởi chạy:
- Đường dẫn: `https://localhost:8443/nifi`
- Tài khoản: `admin`
- Mật khẩu: `BigData2026Password!`

## 2. Các Processor trong Dataflow Graph
Quy trình luân chuyển dữ liệu từ nguồn tuyển dụng đến Hadoop HDFS bao gồm 3 Processors chính:

1. **`ExecuteProcess` Processor**:
   - **Command**: `python`
   - **Command Arguments**: `/opt/nifi/nifi-current/crawler/run_crawler.py --pages 3`
   - **Run Schedule**: `0 0 12 * * ?` (Lập lịch Cron kích hoạt mỗi ngày vào 12h trưa)
   - **Vai trò**: Tự động chạy script cào tin tuyển dụng từ các trang web IT tại Việt Nam.

2. **`EvaluateJsonPath` & `SplitJson` Processors**:
   - **Destination**: flowfile-attribute
   - **Vai trò**: Bóc tách và kiểm tra tính hợp lệ của mảng JSON trước khi lưu trữ.

3. **`PutHDFS` Processor**:
   - **Hadoop Configuration Resources**: `/etc/hadoop/core-site.xml,/etc/hadoop/hdfs-site.xml`
   - **Directory**: `/data/raw/jobs/year=${now():format('yyyy')}/month=${now():format('MM')}/day=${now():format('dd')}/`
   - **Conflict Resolution Strategy**: replace
   - **Vai trò**: Ghi tệp FlowFile JSON vào Hadoop HDFS Raw Zone để bảo toàn dữ liệu gốc.
