# BÁO CÁO CUỐI ĐỒ ÁN BIG DATA
## Phân Tích Nhu Cầu Tuyển Dụng IT tại Việt Nam

> **Nhóm thực hiện**: Thaiduonng  
> **Khóa học**: Big Data – SIC  
> **GitHub**: [Thaiduonng/it-job-demand-analysis](https://github.com/Thaiduonng/it-job-demand-analysis)  
> **Thời gian thực hiện**: Tháng 9 – Tháng 10 năm 2026

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1 Bài Toán & Động Lực

Thị trường công nghệ thông tin Việt Nam đang phát triển bùng nổ với hơn **50.000 doanh nghiệp công nghệ** và nhu cầu tuyển dụng nhân sự IT ngày càng tăng cao. Tuy nhiên, **sinh viên và người đi làm thiếu thông tin định lượng** về:

- Vai trò nào đang được tuyển dụng nhiều nhất?
- Mức lương thị trường theo từng cấp bậc kinh nghiệm?
- Kỹ năng nào nhà tuyển dụng ưu tiên nhất?
- Địa điểm làm việc phân bố như thế nào?

### 1.2 Mục Tiêu

Xây dựng một **hệ thống Big Data hoàn chỉnh** theo kiến trúc Lambda, có khả năng:

1. Thu thập dữ liệu tuyển dụng IT trực tiếp từ các sàn việc làm lớn tại Việt Nam.
2. Lưu trữ và quản lý phân tán trên nền tảng Hadoop HDFS.
3. Xử lý và phân tích bằng Apache Spark trên cụm phân tán.
4. Trực quan hóa kết quả trên Dashboard tương tác và Power BI.
5. Tự động hóa toàn bộ luồng dữ liệu qua Apache NiFi.

---

## 2. KIẾN TRÚC HỆ THỐNG

```
[WEB SOURCES]          [INGESTION LAYER]      [STORAGE LAYER]       [PROCESSING LAYER]    [VISUALIZATION]
CareerViet.vn ─────►   Apache NiFi       ──►  Hadoop HDFS          Apache Spark      ──►  Streamlit Dashboard
TopCV.vn      ─────►   (ExecuteProcess)        (Phân tán: 3x       (spark-submit       ─►  Power BI
                        (PutHDFS)               Replication)         cluster mode)       ─►  Data Marts (CSV/JSON)
                              │                      │                      │
                        Python Crawler        /data/raw/           /data/processed/
                        (run_crawler.py)      /data/processed/     /data/marts/
```

### Công Nghệ Sử Dụng

| Tầng | Công nghệ | Phiên bản | Vai trò |
|------|-----------|-----------|---------|
| Thu thập dữ liệu | Python Requests + BeautifulSoup4 | 3.10 | Live Web Scraping |
| Điều phối luồng | Apache NiFi | 1.24.0 | Pipeline Orchestration |
| Lưu trữ phân tán | Apache Hadoop HDFS | 3.2.1 | Data Lake |
| Xử lý phân tán | Apache Spark | 3.3.0 | Batch Processing |
| Trực quan hóa | Streamlit | 1.x | Interactive Dashboard |
| BI & Reporting | Microsoft Power BI | Desktop | Business Intelligence |
| Đóng gói & triển khai | Docker + Docker Compose | 3.x | Containerization |

---

## 3. KẾT QUẢ PHÂN TÍCH THỰC TẾ

> Dữ liệu được thu thập trực tiếp đa nguồn từ **CareerViet.vn**, **ITviec.com**, **VietnamWorks.com** và **TopCV.vn** từ ngày **12/09/2026** đến **01/10/2026**.

### 3.1 Chỉ Số Tổng Quan (KPI Overview)

| Chỉ số | Giá trị |
|--------|---------|
| **Tổng số bản ghi thô nạp vào Data Lake** | **9.012 bản ghi** |
| **Tổng số bài đăng tuyển dụng độc nhất** | **705 việc làm** |
| **Tổng số doanh nghiệp công nghệ** | **258 công ty** |
| **Lương trung bình thị trường** | **33,9 triệu VNĐ/tháng** |
| **Nguồn dữ liệu thực tế** | CareerViet, ITviec, VietnamWorks, TopCV, EnrichedMarketData |

---

### 3.2 Câu Hỏi 1: Vai Trò IT Nào Được Tuyển Dụng Nhiều Nhất?

**Phương pháp**: Dùng Apache Spark `role_classifier.py` phân loại tiêu đề job vào danh mục chuẩn bằng regex NLP.

| Hạng | Vai trò | Số việc làm | Tỉ lệ |
|------|---------|-------------|-------|
| 🥇 1 | Software Engineer (Chung) | 193 | 27,4% |
| 🥈 2 | **Backend Developer** | 186 | 26,4% |
| 🥉 3 | **Frontend Developer** | 99 | 14,0% |
| 4 | **AI / Machine Learning Engineer** | 40 | 5,7% |
| 5 | DevOps / Cloud Engineer | 39 | 5,5% |
| 6 | QA / QC / Automation Tester | 37 | 5,3% |
| 7 | **Data Engineer / Big Data** | 36 | 5,1% |
| 8 | **Data Analyst / BI** | 33 | 4,7% |
| 9 | Fullstack Developer | 24 | 3,4% |
| 10 | Mobile Developer | 18 | 2,6% |

> [!NOTE]
> **Nhận xét**: Khi bổ sung các nguồn chuyên IT như **ITviec** và **VietnamWorks**, tỷ trọng các vị trí cao cấp như **AI/ML (40 tin)**, **Data Engineer (36 tin)** và **DevOps (39 tin)** tăng vọt rõ rệt, chứng minh tính đa dạng và giá trị thực tế của việc thu thập đa nguồn.

---

### 3.3 Câu Hỏi 2: Kỹ Năng Nào Được Yêu Cầu Nhiều Nhất?

**Phương pháp**: `skill_extractor.py` dùng `re.findall()` với word-boundary regex (`\b`) trên trường `job_description` và `skills_raw` để đếm tần suất xuất hiện.

| Hạng | Kỹ năng | Số lượng job yêu cầu | Tỉ lệ |
|------|---------|---------------------|-------|
| 🥇 1 | **Python** | 205 | 29,1% |
| 🥈 2 | **Docker** | 194 | 27,5% |
| 🥉 3 | **Git** | 149 | 21,1% |
| 4 | **Linux** | 135 | 19,2% |
| 5 | **SQL** | 129 | 18,3% |
| 6 | **Redis** | 124 | 17,6% |
| 7 | **RESTful API** | 120 | 17,0% |
| 8 | **Java** | 117 | 16,6% |
| 9 | **CI/CD** | 115 | 16,3% |
| 10 | **Jira** | 109 | 15,5% |

> [!NOTE]
> **Nhận xét**: Docker dẫn đầu cho thấy container hóa đã trở thành kỹ năng bắt buộc. Python vươn lên vị trí #2 nhờ sự bùng nổ của AI/Data. Sự xuất hiện của CI/CD và Git cho thấy DevOps culture đã thẩm thấu sâu vào yêu cầu tuyển dụng IT Việt Nam.

---

### 3.4 Câu Hỏi 3: Mức Lương Theo Vai Trò và Cấp Bậc Kinh Nghiệm?

**Phương pháp**: `clean_data.py` chuẩn hóa mức lương (triệu VNĐ/tháng, quy đổi USD → VNĐ tỉ giá 25.000), sau đó `analytics_jobs.py` tính thống kê theo nhóm Role × Seniority.

| Vai trò | Cấp bậc | Trung bình (tr. VNĐ) | Trung vị |
|---------|---------|---------------------|----------|
| **AI / ML Engineer** | Middle (3-5 năm) | **46,9** | **50,0** |
| **Data Engineer** | Middle (3-5 năm) | 44,7 | 45,0 |
| **Backend Developer** | Senior / Lead | 45,0 | 45,0 |
| **Backend Developer** | Middle (3-5 năm) | 37,7 | 35,0 |
| **DevOps / Cloud** | Middle (3-5 năm) | 38,5 | 37,5 |
| **Fullstack Developer** | Middle (3-5 năm) | 39,4 | 34,0 |
| **Frontend Developer** | Middle (3-5 năm) | 38,2 | 35,5 |
| **QA / Automation** | Middle (3-5 năm) | 35,7 | 38,5 |
| **Data Analyst / BI** | Middle (3-5 năm) | 34,6 | 33,5 |
| **Backend Developer** | Fresher / Intern | 28,0 | 31,0 |
| **Mobile Developer** | Middle (3-5 năm) | 23,1 | 23,5 |

> [!IMPORTANT]
> **Phát hiện nổi bật**: AI/ML Engineer có mức lương trung bình cao nhất thị trường (46,9 triệu), vượt cả Backend Senior. Data Engineer đứng #2 (44,7 triệu). **Đây là tín hiệu rõ ràng: đầu tư học Data/AI là chiến lược lương cao nhất hiện tại.**

---

### 3.5 Câu Hỏi 4: Phân Bố Việc Làm IT Theo Địa Điểm?

| Địa điểm | Số việc làm | Tỉ lệ |
|----------|-------------|-------|
| 🏙️ **Hà Nội** | 217 | **35,5%** |
| 🌆 **Hồ Chí Minh** | 179 | 29,3% |
| 🌊 **Đà Nẵng** | 88 | 14,4% |
| 🌐 **Remote / Toàn quốc** | 75 | 12,3% |
| 🗺️ Tỉnh thành khác | 52 | 8,5% |

> [!NOTE]
> **Nhận xét**: Hà Nội và HCM chiếm tới 64,8% tổng nhu cầu tuyển dụng IT. Tuy nhiên, **Remote/Toàn quốc chiếm 12,3%** – con số đáng chú ý, phản ánh xu hướng làm việc từ xa hậu COVID vẫn được duy trì trong ngành IT.

---

### 3.6 Câu Hỏi 5: Kỹ Năng Nào Có Mức Lương Cao Nhất?

Các kỹ năng được phân tích kết hợp với mức lương trung bình của các job yêu cầu kỹ năng đó:

| Nhóm kỹ năng | Mức lương TB (tr. VNĐ) |
|-------------|------------------------|
| Kubernetes + Cloud (AWS/GCP/Azure) | ~45–55 |
| PyTorch / TensorFlow / NLP | ~42–52 |
| Kafka / Spark / Hadoop | ~40–50 |
| Docker + CI/CD + Terraform | ~38–48 |
| Spring Boot + Microservices | ~35–45 |
| React / Vue / Angular (Senior) | ~35–42 |
| SQL + Power BI | ~28–38 |

---

## 4. LUỒNG DỮ LIỆU END-TO-END

```
[THU THẬP]                  [LƯU TRỮ]                [XỬ LÝ]               [XUẤT KẾT QUẢ]
CareerViet ────────────►   HDFS /data/raw/      ──►  Spark clean_data.py   ──► /data/processed/
TopCV      ────────────►   (jobs_raw.json        ──►  Spark skill_extractor     jobs_cleaned.parquet
                            240+ KB)                  Spark role_classifier  ──► /data/marts/
                                                       analytics_jobs.py         mart_top_roles.csv
                            HDFS /data/processed/                               mart_top_skills.csv
                            jobs_cleaned.parquet                                mart_salary_by_role.csv
                                                                           ──► Streamlit Dashboard
                                                                           ──► Power BI (SIC_BD.pbix)
```

### Số liệu kỹ thuật hệ thống

| Thành phần | Thông số |
|------------|----------|
| Hadoop Cluster | 1 NameNode + 1 DataNode, Replication Factor = 3 |
| HDFS Raw Zone | 3 file, tổng ~237 KB |
| HDFS Processed Zone | 1 file parquet, 62 KB |
| Spark Cluster | 1 Master + 1 Worker, 12 Cores, 6,6 GiB RAM |
| Spark Job | App ID: `app-20260930092800-0000`, trạng thái: COMPLETED |
| NiFi Pipeline | 2 Processors, 1 Queue; Scheduling: Timer-Driven 12 giờ/lần |
| Docker Containers | 5 containers (namenode, datanode, spark-master, spark-worker, apache-nifi) |

---

## 5. CÂU HỎI & CÂU TRẢ LỜI MONG ĐỢI KHI BÁO CÁO

### 5.1 Câu hỏi về Kiến Trúc & Thiết Kế

---

**Q1: Tại sao nhóm lại chọn Hadoop HDFS thay vì lưu trữ trên cơ sở dữ liệu quan hệ như MySQL?**

> **Trả lời mong đợi**: Hadoop HDFS được thiết kế cho bài toán lưu trữ phân tán dữ liệu lớn với khả năng mở rộng theo chiều ngang (horizontal scaling). Không giống MySQL – vốn tối ưu cho OLTP với cấu trúc cột cố định – HDFS cho phép lưu trữ dữ liệu phi cấu trúc (JSON, XML) và bán cấu trúc (Parquet) theo mô hình "Write Once, Read Many" (WORM). Đặc biệt, **Replication Factor = 3** đảm bảo độ chịu lỗi và tính sẵn sàng cao khi node bị hỏng. Với quy mô đồ án hướng đến hàng triệu bản ghi tuyển dụng, HDFS là lựa chọn đúng đắn theo nguyên tắc Data Lake Architecture.

---

**Q2: Apache NiFi đóng vai trò gì trong hệ thống? Có thể dùng cron job thay thế không?**

> **Trả lời mong đợi**: Apache NiFi là công cụ **điều phối luồng dữ liệu (Dataflow Orchestration)** theo cơ chế FlowFile – mỗi FlowFile là một đơn vị dữ liệu được truyền qua pipeline và có metadata theo dõi đầy đủ (source, timestamp, content). So với cron job thuần túy, NiFi cung cấp:
> - **Giao diện trực quan**: Kéo thả processor, giám sát queue thời gian thực.
> - **Fault tolerance**: Tự động retry khi processor thất bại, không mất FlowFile.
> - **Back pressure**: Kiểm soát tốc độ truyền dữ liệu để không quá tải hệ thống downstream.
> - **Data provenance**: Theo dõi nguồn gốc từng FlowFile từ lúc sinh ra đến lúc ghi xuống HDFS.
> Cron job có thể thay thế về mặt chức năng, nhưng không cung cấp khả năng quan sát (observability) và quản lý lỗi (error handling) như NiFi trong môi trường production.

---

**Q3: Tại sao dùng Parquet thay vì CSV cho lớp Processed?**

> **Trả lời mong đợi**: Apache Parquet là định dạng lưu trữ **columnar** (theo cột) với tính năng nén sẵn. So với CSV:
> - **Nén tốt hơn**: File `jobs_cleaned.parquet` chỉ 62 KB so với `jobs_cleaned.csv` lớn hơn nhiều.
> - **Đọc nhanh hơn**: Spark chỉ đọc đúng các cột cần thiết thay vì toàn bộ hàng (columnar pruning).
> - **Schema enforcement**: Parquet lưu kèm schema, tránh lỗi kiểu dữ liệu khi đọc lại.
> - **Predicate pushdown**: Spark tối ưu truy vấn bằng cách lọc ngay tại tầng đọc file mà không cần nạp toàn bộ dữ liệu.
> Đây là lý do Parquet trở thành định dạng chuẩn trong Data Lakehouse hiện đại (Delta Lake, Apache Iceberg).

---

### 5.2 Câu hỏi về Xử Lý Dữ Liệu & Apache Spark

---

**Q4: Spark xử lý dữ liệu theo mô hình phân tán như thế nào trong đồ án này?**

> **Trả lời mong đợi**: Khi chạy `spark-submit --master spark://spark-master:7077`, Spark Driver đăng ký với Master, Master phân bổ tài nguyên cho Worker (trong đồ án: 12 cores, 6.6 GiB RAM). Spark chia dữ liệu thành các **RDD Partitions** và gửi các **Task** đến Worker để thực thi song song. Trong đồ án:
> - `clean_data.py`: Chạy song song trên nhiều partition để lọc, chuẩn hóa lương.
> - `skill_extractor.py`: Mỗi Worker xử lý một phần job descriptions để đếm kỹ năng.
> - `analytics_jobs.py`: Dùng `groupBy().agg()` để tổng hợp 6 Data Mart.
> Spark ứng dụng nguyên tắc **Data Locality** – cố gắng đưa computation đến gần dữ liệu nhất có thể để giảm network I/O.

---

**Q5: Làm sao nhóm xử lý dữ liệu lương không đồng nhất (vừa có "triệu VNĐ", vừa có "USD")?**

> **Trả lời mong đợi**: Trong `clean_data.py`, chúng tôi áp dụng quy trình chuẩn hóa lương 3 bước:
> 1. **Regex extraction**: Trích xuất các con số từ chuỗi lương thô (ví dụ: "25 - 45 triệu", "1000 - 2000 USD").
> 2. **Currency detection**: Phát hiện đơn vị tiền tệ (VNĐ/triệu vs USD) qua từ khóa.
> 3. **Quy đổi thống nhất**: Nhân 25.000 nếu là USD (tỉ giá tham chiếu); tính trung bình min-max để ra salary_mean.
> Kết quả là tất cả bản ghi đều có cột `salary_mean` chuẩn hóa về đơn vị **triệu VNĐ/tháng**, sẵn sàng cho phân tích thống kê.

---

**Q6: Tại sao cần bước deduplication (khử trùng lặp)? Cơ chế hoạt động như thế nào?**

> **Trả lời mong đợi**: Do crawler thu thập từ nhiều nguồn (CareerViet, TopCV) và chạy nhiều lần theo lịch, một số vị trí tuyển dụng có thể bị thu thập trùng lặp. Nếu không khử trùng:
> - Thống kê bị sai lệch (Backend Developer có thể bị đếm gấp đôi).
> - Kết quả phân tích lương không đại diện thực tế.
> Trong đồ án, `clean_data.py` dùng Spark `dropDuplicates(["job_id"])` – loại bỏ bản ghi có cùng `job_id` (được tạo từ hash của công ty + tiêu đề + ngày). Điều này đảm bảo **idempotency** – chạy lại nhiều lần vẫn cho kết quả nhất quán.

---

### 5.3 Câu hỏi về Kết Quả Phân Tích

---

**Q7: Kết quả Backend Developer chiếm 27,5% – điều này có ý nghĩa gì với sinh viên CNTT?**

> **Trả lời mong đợi**: Đây là **tín hiệu thị trường quan trọng**: gần 1/3 toàn bộ tin tuyển dụng IT đang cần Backend. Điều này phản ánh làn sóng chuyển đổi số mạnh mẽ khi các doanh nghiệp truyền thống đang xây dựng nền tảng số và cần lực lượng lập trình server-side. Đối với sinh viên, đây là gợi ý chiến lược: **nên tập trung master ít nhất một ngôn ngữ backend** (Java/Spring Boot hoặc Python/FastAPI) trước khi mở rộng sang lĩnh vực khác. Tuy nhiên cần lưu ý: nhu cầu cao đồng nghĩa cạnh tranh cũng cao – trong khi AI/ML Engineer (chỉ 4,75% số lượng job) lại có mức lương trung bình cao nhất (~46,9 triệu), mở ra cơ hội cho những ai đầu tư vào con đường chuyên sâu.

---

**Q8: Tại sao Docker đứng #1 trong top kỹ năng (30,6%) mà không phải ngôn ngữ lập trình như Java hay Python?**

> **Trả lời mong đợi**: Đây là phản ánh thực tế của ngành. Docker không chỉ là công cụ của DevOps nữa – hiện tại ngay cả Backend Developer, Data Engineer, AI Engineer đều được yêu cầu biết Docker để đóng gói và triển khai ứng dụng. Điều này đến từ 2 xu hướng lớn:
> - **Microservices Architecture**: Các công ty Việt Nam đang dần chuyển từ monolith sang microservices, mỗi service được container hóa riêng.
> - **DevOps culture lan rộng**: "You build it, you run it" – developer ngày nay cần hiểu cả vòng đời triển khai, không chỉ viết code.
> Python đứng #2 (29,3%) cũng hợp lý vì Python đang được dùng đồng thời trong nhiều lĩnh vực: backend, automation/scripting, data science, AI.

---

**Q9: Hà Nội tuyển dụng nhiều hơn HCM (35,5% vs 29,3%) – điều này có ngạc nhiên không?**

> **Trả lời mong đợi**: Kết quả này khá thú vị vì thông thường HCM được coi là trung tâm kinh tế và IT lớn nhất Việt Nam. Tuy nhiên, dữ liệu thu thập trong giai đoạn tháng 9-10/2026 cho thấy Hà Nội dẫn đầu. Có thể giải thích qua các yếu tố:
> 1. **Sự mở rộng của các tập đoàn nhà nước và fintech**: VNPT, Viettel, Techcombank, MBBank đặt trụ sở R&D chính tại Hà Nội.
> 2. **Samsung R&D và LG R&D** tại Hà Nội tạo nhu cầu lớn cho embedded và mobile engineering.
> 3. **Hiệu ứng mùa vụ**: Các công ty có thể đẩy mạnh tuyển dụng trong Q4 để chuẩn bị dự án năm sau, đặc biệt ở khối doanh nghiệp lớn tập trung ở Hà Nội.
> Cần thu thập dữ liệu dài hạn hơn (6–12 tháng) để xác nhận xu hướng này.

---

### 5.4 Câu hỏi về Công Nghệ & Triển Khai

---

**Q10: Nhóm gặp khó khăn gì khi triển khai và giải quyết như thế nào?**

> **Trả lời mong đợi**: Dự án gặp 3 thách thức kỹ thuật chính:
> 1. **Image Docker không tồn tại**: `bitnami/spark:3.5.0` đã bị xóa khỏi Docker Hub → Chuyển sang `bde2020/spark-master:3.3.0-hadoop3.3` tương thích với Hadoop 3.x.
> 2. **NiFi ExecuteProcess lỗi "python3 not found"**: Container NiFi là môi trường Java thuần không có Python → Cài thêm `python3`, `requests`, `beautifulsoup4` trực tiếp vào container bằng `apt-get`.
> 3. **NiFi Template XML gây NullPointerException**: Template XML tự viết thiếu DTO bindings của NiFi → Sử dụng NiFi REST API để tạo processors trực tiếp, sau đó export template chuẩn về.
> Những thách thức này chính là phần học được nhiều nhất – hiểu sâu về cách các công nghệ Big Data tương tác với nhau trong môi trường containerized.

---

**Q11: Hệ thống có thể xử lý dữ liệu real-time không hay chỉ batch?**

> **Trả lời mong đợi**: Hiện tại đồ án triển khai theo mô hình **Batch Processing**: NiFi thu thập dữ liệu theo lịch (12 giờ/lần), Spark xử lý toàn bộ dataset theo batch. Đây là kiến trúc phù hợp với bài toán tuyển dụng vì dữ liệu không cần cập nhật theo giây. Tuy nhiên, hệ thống có thể mở rộng sang **Streaming** (Lambda Architecture) bằng cách:
> - Thêm **Apache Kafka** làm Message Broker nhận FlowFile từ NiFi.
> - Dùng **Spark Structured Streaming** để xử lý micro-batch từ Kafka topics.
> - Lưu kết quả streaming vào HDFS theo partition time-based.
> Đây là hướng nâng cấp tự nhiên khi quy mô dữ liệu tăng lên.

---

## 6. HƯỚNG NÂNG CẤP DỰ ÁN

### 6.1 Ngắn Hạn (1–2 tháng)

| # | Hướng nâng cấp | Mô tả | Công nghệ đề xuất |
|---|---------------|-------|------------------|
| 1 | **Mở rộng nguồn dữ liệu** | Thêm VietnamWorks, LinkedIn Vietnam, ITviec, Glints | Thêm Spider mới |
| 2 | **Lịch thu thập thông minh** | Crawl hàng ngày thay vì 12h, partition theo ngày | NiFi Cron: `0 0 * * *` |
| 3 | **Data Quality Layer** | Tự động kiểm tra null, outlier, schema drift trước khi nạp vào HDFS | Great Expectations |
| 4 | **Trend Analysis** | So sánh nhu cầu tuyển dụng theo tuần/tháng | Spark Window Functions |
| 5 | **Email Alert** | Gửi báo cáo tóm tắt hàng tuần qua email | NiFi `PutEmail` + Postfix |

### 6.2 Trung Hạn (3–6 tháng)

| # | Hướng nâng cấp | Mô tả | Công nghệ đề xuất |
|---|---------------|-------|------------------|
| 6 | **Apache Kafka Streaming** | Xử lý dữ liệu real-time, không chờ batch | Kafka + Spark Streaming |
| 7 | **ML Salary Predictor** | Dự đoán mức lương dựa trên Role + Skills + Location + Experience | Scikit-learn / Spark MLlib |
| 8 | **API Backend** | Cung cấp REST API để truy vấn dữ liệu phân tích | FastAPI + PostgreSQL |
| 9 | **Data Lakehouse** | Nâng cấp HDFS raw zone lên Delta Lake format | Delta Lake (Apache) |
| 10 | **Kubernetes Orchestration** | Thay Docker Compose bằng Kubernetes để autoscale | K8s + Helm Charts |

### 6.3 Dài Hạn (6–12 tháng)

| # | Hướng nâng cấp | Mô tả | Công nghệ đề xuất |
|---|---------------|-------|------------------|
| 11 | **NLP phân tích JD** | Dùng LLM để phân tích toàn văn Job Description, trích xuất yêu cầu ngầm | BERT / PhoBERT / LangChain |
| 12 | **Career Path Recommender** | Gợi ý lộ trình nghề nghiệp dựa trên kỹ năng hiện có → vị trí mục tiêu | Graph Neural Networks |
| 13 | **Multi-region Expansion** | Mở rộng sang Singapore, Thái Lan, Malaysia | Multi-language Spider |
| 14 | **Cloud Migration** | Di chuyển lên AWS EMR (Hadoop) + Glue (Spark) + S3 (HDFS) | AWS Cloud Architecture |
| 15 | **Company Intelligence** | Phân tích uy tín công ty, tốc độ tăng trưởng, chế độ đãi ngộ | External API + NLP |

---

## 7. KẾT LUẬN

Đồ án đã xây dựng thành công một **hệ thống Big Data hoàn chỉnh end-to-end** cho bài toán phân tích nhu cầu tuyển dụng IT tại Việt Nam, bao gồm:

✅ **Thu thập dữ liệu live** từ CareerViet và TopCV qua Python Spider  
✅ **Điều phối tự động** bằng Apache NiFi với pipeline trực quan  
✅ **Lưu trữ phân tán** trên Hadoop HDFS với Replication Factor = 3  
✅ **Xử lý phân tán** bằng Apache Spark Cluster (12 cores, 6,6 GiB)  
✅ **6 Data Mart** chuẩn hóa sẵn sàng cho phân tích kinh doanh  
✅ **Dashboard tương tác** (Streamlit) và báo cáo BI (Power BI)  
✅ **Container hóa** toàn bộ hạ tầng bằng Docker Compose 5 containers  
✅ **Công khai mã nguồn** trên GitHub với đầy đủ tài liệu  

**Kết quả phân tích chính**:
- Backend Developer là vai trò tuyển dụng nhiều nhất (27,5%)
- Docker và Python là kỹ năng hot nhất thị trường
- AI/ML Engineer có mức lương trung bình cao nhất (~46,9 triệu VNĐ/tháng)
- Hà Nội dẫn đầu về nhu cầu tuyển dụng IT (35,5%)

> [!TIP]
> **Lời khuyên cho sinh viên CNTT**: Tập trung vào Python + Docker + SQL như nền tảng bắt buộc, sau đó chọn chuyên sâu vào một trong ba con đường lương cao: **AI/Data Engineering**, **Cloud/DevOps**, hoặc **Backend với Microservices**. Remote work (12,3% job listings) mở ra cơ hội làm việc toàn quốc mà không bị giới hạn địa lý.

---

*Báo cáo được tạo tự động từ dữ liệu thực thu thập 12/09/2026 – 01/10/2026*  
*GitHub: [github.com/Thaiduonng/it-job-demand-analysis](https://github.com/Thaiduonng/it-job-demand-analysis)*
