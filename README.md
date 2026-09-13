# Hệ Thống Phân Tích Nhu Cầu Tuyển Dụng Ngành CNTT Tại Việt Nam

**Dự án môn học:** Dữ Liệu Lớn (Big Data)  
**Công nghệ cốt lõi:** Python Web Crawler, Apache NiFi, Hadoop HDFS, Apache Spark (PySpark), Power BI Desktop / Streamlit Dashboard.

---

## 1. Kiến Trúc Hệ Thống (Pipeline Architecture)

Hệ thống được thiết kế theo mô hình **Batch Processing Pipeline kết hợp Data Lakehouse đa vùng**, tuân thủ nghiêm ngặt theo **Đề cương đồ án (Chương 3)**:

```
[Các Website Tuyển Dụng IT: CareerViet, TopCV...]
                    │
                    ▼  (Python Spiders / BeautifulSoup / Requests)
[Dữ Liệu Tuyển Dụng Thô (HTML/JSON)]
                    │
                    ▼  (Cron-job Orchestration / Packaging FlowFiles)
[Apache NiFi (Dataflow)]
                    │
                    ▼  (PutHDFS Processor)
[Hadoop HDFS - Raw Zone (/data/raw/)]
                    │
                    ▼  (PySpark Distributed Processing Engine)
[Apache Spark: Khử trùng lặp, Chuẩn hóa Lương VND, Trích xuất Kỹ năng, Phân loại Vai trò]
                    │
                    ├─────────────────────────────────────────┐
                    ▼                                         ▼
[Hadoop HDFS - Processed Zone (/data/processed/)]   [Data Marts Phân Tích (/data/marts/)]
(Định dạng Parquet nén Snappy)                       (CSV / JSON phục vụ BI)
                    │                                         │
                    ▼                                         ▼
            [Spark SQL Queries]                     [Power BI Desktop & Web Dashboard]
```

---

## 2. Cấu Trúc Thư Mục Dự Án

```
d:/BigData-SIC/
├── crawler/                # Module thu thập dữ liệu tuyển dụng IT trực tiếp
│   ├── spiders/            # Kịch bản cào (CareerViet, TopCV)
│   ├── config.py           # Cấu hình headers, địa bàn, từ khóa
│   └── run_crawler.py      # Điều phối cào và đóng gói dữ liệu thô
├── nifi/                   # Cấu hình Apache NiFi
│   ├── flows/              # Hướng dẫn và cấu hình đồ thị NiFi Dataflow
│   └── cron_trigger.py     # Script mô phỏng bộ kích hoạt NiFi Flow
├── hdfs/                   # Quản lý kho dữ liệu phân tán Hadoop HDFS & Local Lake
│   └── hdfs_manager.py     # Dual-mode HDFS Manager (Cluster & Local Lake)
├── spark/                  # Trái tim tính toán phân tán Apache Spark
│   ├── clean_data.py       # Khử trùng lặp, chuẩn hóa lương VND, kinh nghiệm
│   ├── skill_extractor.py  # Regex biên từ trích xuất từ điển Tech Stack IT
│   ├── role_classifier.py  # Phân loại vị trí (Backend, AI, DevOps, Data...)
│   ├── analytics_jobs.py   # Thực thi 5 bài toán phân tích & xuất Data Marts
│   └── run_pipeline.py     # Kịch bản điều phối toàn bộ luồng Spark
├── docker/                 # Hạ tầng cụm Docker Compose
│   ├── docker-compose.yml  # NameNode, DataNode, Spark Master/Worker, NiFi
│   └── hadoop.env          # Biến môi trường cụm Hadoop
├── bi_dashboard/           # Trực quan hóa dữ liệu
│   ├── powerbi/            # Hướng dẫn kết nối và công thức DAX Power BI
│   └── web_dashboard.py    # Web Dashboard tương tác (Streamlit & Plotly)
├── data/                   # Kho dữ liệu Data Lake
│   ├── raw/                # Dữ liệu thô ban đầu (JSON/JSONL)
│   ├── processed/          # Dữ liệu sau xử lý (Parquet & CSV)
│   └── marts/              # Các bảng tổng hợp phục vụ báo cáo
├── requirements.txt        # Danh mục thư viện phụ thuộc
├── Đề cương.docx           # Đề cương chi tiết đồ án môn học
└── README.md               # Tài liệu hướng dẫn sử dụng
```

---

## 3. Hướng Dẫn Cài Đặt & Chạy Demo

### Bước 1: Cài đặt các thư viện cần thiết
```bash
py -3.11 -m pip install -r requirements.txt
```

### Bước 2: Thu thập dữ liệu tuyển dụng trực tiếp (Ingestion)
Chạy script cào dữ liệu từ các website tuyển dụng IT:
```bash
py -3.11 crawler/run_crawler.py --pages 3 --records 300
```
*Dữ liệu thô sẽ được lưu trữ tự động vào `data/raw/` theo định dạng JSON & JSONL.*

### Bước 3: Đưa dữ liệu vào Hadoop HDFS (NiFi Trigger)
Kích hoạt luồng Ingestion mô phỏng Apache NiFi đưa dữ liệu thô vào HDFS Raw Zone:
```bash
py -3.11 nifi/cron_trigger.py
```

### Bước 4: Chạy Pipeline Xử Lý & Phân Tích Apache Spark
Chạy quá trình làm sạch dữ liệu, bóc tách kỹ năng, phân loại vị trí và giải quyết 5 bài toán phân tích:
```bash
py -3.11 spark/run_pipeline.py
```
*Dữ liệu sạch sẽ được lưu trữ dưới định dạng Parquet tại `data/processed/jobs_cleaned.parquet` và các bảng Data Marts được sinh ra tại `data/marts/`.*

### Bước 5: Xem Báo Cáo Trực Quan Hóa (Dashboard)

#### Cách 1: Chạy Web Dashboard Tương Tác (Khuyên dùng khi demo báo cáo)
```bash
py -3.11 -m streamlit run bi_dashboard/web_dashboard.py
```
*Trình duyệt sẽ tự động mở trang Dashboard đa chiều với đầy đủ 4 phân hệ (Tổng quan, Kỹ năng, Lương, Khám phá dữ liệu).*

#### Cách 2: Kết nối với Microsoft Power BI Desktop
1. Mở **Power BI Desktop**.
2. Chọn **Get Data** -> **Text/CSV**.
3. Chọn các file trong thư mục `d:\BigData-SIC\data\marts\` hoặc `data\processed\jobs_cleaned.csv`.
4. Xem hướng dẫn chi tiết và các công thức DAX trong [bi_dashboard/powerbi/powerbi_export_guide.md](bi_dashboard/powerbi/powerbi_export_guide.md).

---

## 4. Năm (05) Bài Toán Phân Tích Trọng Tâm (Chương 3.3)

1. **Top Kỹ Năng Phổ Biến:** Tần suất xuất hiện của các ngôn ngữ (Java, Python, C#, Golang...), framework (React, Spring Boot, Node.js...) và nền tảng đám mây/dữ liệu lớn (AWS, Docker, Kubernetes, Spark, Kafka).
2. **Top Vị Trí Tuyển Dụng:** Tỷ lệ nhu cầu thị trường giữa Backend, Frontend, Fullstack, Mobile, DevOps, AI / Data Engineer...
3. **Phân Bố Địa Lý Việc Làm:** Tỷ lệ phân bổ công việc CNTT tại các trung tâm kinh tế lớn (Hà Nội, TP. Hồ Chí Minh, Đà Nẵng, Remote).
4. **Mức Lương Theo Vị Trí & Cấp Bậc Kinh Nghiệm:** Thống kê Min, Max, Trung bình (Mean), Trung vị (Median) theo các nấc kinh nghiệm (Fresher/Intern, Junior, Middle, Senior/Lead).
5. **Kỹ Năng Thu Nhập Cao:** Bảng xếp hạng các công nghệ và kỹ năng đem lại mức lương trung bình cao nhất tại thị trường Việt Nam.

---

## 5. Triển Khai Cụm Docker Compose (Hadoop + Spark + NiFi)

Khi cần triển khai toàn bộ hệ sinh thái trên Docker Cluster:
```bash
cd docker
docker-compose up -d
```
- **Hadoop NameNode Web UI:** `http://localhost:9870`
- **Spark Master Web UI:** `http://localhost:8080`
- **Apache NiFi Web UI:** `https://localhost:8443/nifi`
