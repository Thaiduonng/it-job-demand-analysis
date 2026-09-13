# Hướng Dẫn Kết Nối Power BI & Thiết Kế Dashboard

Tài liệu này hướng dẫn chi tiết cách kết nối **Power BI Desktop** với kho dữ liệu Data Marts được sinh ra từ pipeline Big Data, bám sát **Chương 3.4 của Đề cương đồ án**.

---

## 1. Nguồn Dữ Liệu Data Marts (Gold Layer)
Dữ liệu sau khi xử lý bằng Apache Spark được xuất tự động tại thư mục:
`d:\BigData-SIC\data\marts\`
Hoặc bảng chi tiết tại:
`d:\BigData-SIC\data\processed\jobs_cleaned.csv` / `jobs_cleaned.parquet`

Các bảng dữ liệu chính:
| Tên Tệp | Nội Dung |
|---|---|
| `jobs_cleaned.csv` | Toàn bộ dữ liệu tuyển dụng chi tiết đã làm sạch, bóc tách kỹ năng, lương và vai trò |
| `mart_overview_kpi.csv` | Các chỉ số KPI tổng hợp: Tổng tin tuyển dụng, Số công ty, Lương trung bình |
| `mart_top_skills.csv` | Top các kỹ năng / công nghệ IT được yêu cầu nhiều nhất và tỷ lệ % |
| `mart_top_roles.csv` | Phân bố nhu cầu tuyển dụng theo vai trò chuyên môn (Backend, AI, DevOps...) |
| `mart_location_distribution.csv` | Tỷ lệ phân bố việc làm theo thành phố (Hà Nội, TP.HCM, Đà Nẵng, Remote) |
| `mart_salary_by_role_exp.csv` | Mức lương Min, Max, Trung bình theo từng Vị trí và Cấp bậc kinh nghiệm |
| `mart_skills_salary.csv` | Bảng xếp hạng các kỹ năng công nghệ có thu nhập trung bình cao nhất |

---

## 2. Các Bước Kết Nối Trên Power BI Desktop

1. Mở **Power BI Desktop**.
2. Chọn **Get Data** (Lấy dữ liệu) -> **Text/CSV** (hoặc **Folder** để nạp toàn bộ thư mục `data\marts\`).
3. Điều hướng tới đường dẫn: `d:\BigData-SIC\data\marts\` và chọn các file `.csv` trên.
4. Nhấn **Load** để nạp trực tiếp vào Power BI Data Model.

---

## 3. Các Công Thức DAX Measures Đề Xuất

Tạo một bảng Measure mới (`_Measures`) và thêm các công thức sau:

```dax
// 1. Tổng số việc làm IT
Total_Jobs = COUNTROWS('jobs_cleaned')

// 2. Số lượng công ty tuyển dụng
Total_Companies = DISTINCTCOUNT('jobs_cleaned'[company_name])

// 3. Mức lương trung bình ngành (Triệu VNĐ)
Avg_Salary_Million = ROUND(AVERAGE('jobs_cleaned'[salary_avg]), 1)

// 4. Mức lương trung vị (Triệu VNĐ)
Median_Salary_Million = ROUND(MEDIAN('jobs_cleaned'[salary_avg]), 1)

// 5. Tỷ lệ % tuyển dụng theo từng nhóm
Percent_Jobs = DIVIDE([Total_Jobs], CALCULATE([Total_Jobs], ALL('jobs_cleaned')), 0) * 100
```

---

## 4. Thiết Kế Báo Cáo Trực Quan (3 Phân Hệ Theo Đề Cương)

### Phân hệ 1: Tổng quan thị trường (Overview)
- **Cards KPI**:
  - Thẻ 1: `[Total_Jobs]` (Ví dụ: `300+ Việc làm`).
  - Thẻ 2: `[Total_Companies]` (Ví dụ: `85+ Doanh nghiệp`).
  - Thẻ 3: `[Avg_Salary_Million]` (Ví dụ: `32.5 Triệu VNĐ`).
- **Donut / Pie Chart**: Phân bố việc làm theo `location` (Hà Nội, TP.HCM, Đà Nẵng).
- **Bar Chart (Horizontal)**: Nhu cầu tuyển dụng theo `role_category`.

### Phân hệ 2: Phân tích Kỹ năng (Skills Analysis)
- **Clustered Bar Chart**: Top 15 kỹ năng công nghệ (`skill_name` vs `job_count`).
- **Slicer (Bộ lọc)**: Cho phép chọn theo `role_category` (Ví dụ chọn "Data Engineer / Big Data" thì biểu đồ sẽ hiển thị kỹ năng hàng đầu là Python, Spark, SQL, Kafka, AWS).

### Phân hệ 3: Phân tích Lương & Kinh nghiệm (Salary Insights)
- **Clustered Column Chart**: So sánh `salary_min_avg` và `salary_max_avg` theo `seniority_level` (Fresher -> Junior -> Middle -> Senior).
- **Scatter Plot / Box Plot**: Mối tương quan giữa số năm kinh nghiệm và mức lương thực tế.
- **Top 10 High-Paying Skills**: Biểu đồ cột thể hiện các kỹ năng đem lại mức lương trung bình cao nhất thị trường.
