"""
Interactive Web Dashboard - Phân Tích Nhu Cầu Tuyển Dụng Ngành CNTT Việt Nam
Xây dựng trên Streamlit & Plotly bám sát Chương 3.4 của Đề Cương đồ án.
Cho phép tương tác trực quan, lọc đa chiều và xem báo cáo ngay trên trình duyệt.
"""

import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Đường dẫn thư mục dữ liệu
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MARTS_DIR = DATA_DIR / "marts"
PROCESSED_FILE = DATA_DIR / "processed" / "jobs_cleaned.csv"

def load_data():
    """Nạp dữ liệu đã qua xử lý từ kho Data Lake"""
    if PROCESSED_FILE.exists():
        df = pd.read_csv(PROCESSED_FILE)
        return df
    return pd.DataFrame()

def load_mart(name):
    """Nạp bảng tổng hợp Data Mart"""
    mart_file = MARTS_DIR / f"mart_{name}.csv"
    if mart_file.exists():
        return pd.read_csv(mart_file)
    return pd.DataFrame()

def main():
    import streamlit as st

    st.set_page_config(
        page_title="Vietnam IT Recruitment Analytics - BigData Project",
        page_icon="📊",
        layout="wide"
    )

    # Custom CSS cho giao diện hiện đại, chuyên nghiệp
    st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border-left: 5px solid #2563EB;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1F2937;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #6B7280;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">Hệ Thống Phân Tích Nhu Cầu Tuyển Dụng CNTT Việt Nam</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Đồ án môn học Big Data | Kiến trúc: Web Crawler ➔ Apache NiFi ➔ Hadoop HDFS ➔ Apache Spark ➔ Power BI / Dashboard</div>', unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        st.warning("⚠️ Chưa tìm thấy dữ liệu đã làm sạch trong Data Lake. Hãy chạy pipeline: `python spark/run_pipeline.py` trước!")
        st.stop()

    # Sidebar bộ lọc
    st.sidebar.header("🔍 Bộ Lọc Dữ Liệu Tương Tác")
    all_locations = ["Tất cả"] + sorted(list(df["location_standard"].dropna().unique()))
    selected_loc = st.sidebar.selectbox("Địa bàn tuyển dụng:", all_locations)

    all_roles = ["Tất cả"] + sorted(list(df["role_category"].dropna().unique()))
    selected_role = st.sidebar.selectbox("Vị trí chuyên môn:", all_roles)

    all_seniority = ["Tất cả"] + sorted(list(df["seniority_level"].dropna().unique()))
    selected_seniority = st.sidebar.selectbox("Cấp bậc kinh nghiệm:", all_seniority)

    # Lọc dữ liệu theo lựa chọn
    filtered_df = df.copy()
    if selected_loc != "Tất cả":
        filtered_df = filtered_df[filtered_df["location_standard"] == selected_loc]
    if selected_role != "Tất cả":
        filtered_df = filtered_df[filtered_df["role_category"] == selected_role]
    if selected_seniority != "Tất cả":
        filtered_df = filtered_df[filtered_df["seniority_level"] == selected_seniority]

    # Tabs phân hệ theo đề cương
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 1. Tổng Quan Thị Trường (Overview)",
        "💻 2. Phân Tích Kỹ Năng (Skills Insights)",
        "💰 3. Mức Lương & Kinh Nghiệm (Salary Insights)",
        "🔎 4. Khám Phá Dữ Liệu (Data Explorer)"
    ])

    # ==========================================
    # TAB 1: TỔNG QUAN THỊ TRƯỜNG
    # ==========================================
    with tab1:
        st.subheader("Chỉ Số KPI Toàn Cảnh Tuyển Dụng")
        total_jobs = len(filtered_df)
        total_companies = filtered_df["company_name"].nunique()
        salary_series = filtered_df["salary_avg"].dropna()
        avg_salary = round(salary_series.mean(), 1) if not salary_series.empty else 0.0
        median_salary = round(salary_series.median(), 1) if not salary_series.empty else 0.0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tổng Số Tin Tuyển Dụng", f"{total_jobs:,}")
        col2.metric("Số Doanh Nghiệp Tuyển Dụng", f"{total_companies:,}")
        col3.metric("Mức Lương Trung Bình", f"{avg_salary} Triệu VNĐ" if avg_salary > 0 else "Thỏa thuận")
        col4.metric("Mức Lương Trung Vị (Median)", f"{median_salary} Triệu VNĐ" if median_salary > 0 else "Thỏa thuận")

        st.markdown("---")
        c1, c2 = st.columns([1, 1])

        with c1:
            st.markdown("#### Phân Bố Việc Làm Theo Thành Phố")
            loc_data = filtered_df["location_standard"].value_counts().reset_index()
            loc_data.columns = ["Thành phố", "Số lượng"]
            fig_loc = px.pie(
                loc_data, values="Số lượng", names="Thành phố",
                hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_loc.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_loc, use_container_width=True)

        with c2:
            st.markdown("#### Top Vị Trí Tuyển Dụng Nhiều Nhất")
            role_data = filtered_df["role_category"].value_counts().reset_index()
            role_data.columns = ["Vị trí", "Số lượng"]
            fig_role = px.bar(
                role_data.head(8), x="Số lượng", y="Vị trí", orientation="h",
                color="Số lượng", color_continuous_scale="Blues"
            )
            fig_role.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_role, use_container_width=True)

    # ==========================================
    # TAB 2: PHÂN TÍCH KỸ NĂNG CÔNG NGHỆ
    # ==========================================
    with tab2:
        st.subheader("Báo Cáo Kỹ Năng & Công Nghệ Được Săn Đón")
        
        # Bóc tách kỹ năng từ tập dữ liệu đang lọc
        all_skills = []
        for val in filtered_df["skills"].dropna():
            if isinstance(val, str) and val.startswith("["):
                import ast
                try:
                    skills_list = ast.literal_eval(val)
                except Exception:
                    skills_list = [s.strip() for s in val.strip("[]").replace("'", "").split(",")]
            elif isinstance(val, list):
                skills_list = val
            else:
                skills_list = []
            all_skills.extend(skills_list)

        skill_counts = pd.Series(all_skills).value_counts().reset_index()
        skill_counts.columns = ["Kỹ năng", "Tần suất"]

        if not skill_counts.empty:
            top_k = st.slider("Số lượng kỹ năng hiển thị:", min_value=5, max_value=30, value=15)
            top_skills_df = skill_counts.head(top_k)

            fig_skills = px.bar(
                top_skills_df, x="Kỹ năng", y="Tần suất",
                color="Tần suất", color_continuous_scale="Teal",
                text="Tần suất"
            )
            fig_skills.update_traces(textposition="outside")
            fig_skills.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_skills, use_container_width=True)

            st.markdown("##### Bảng Thống Kê Chi Tiết Tỷ Lệ Kỹ Năng")
            top_skills_df["Tỷ lệ % tin yêu cầu"] = (top_skills_df["Tần suất"] / len(filtered_df) * 100).round(2)
            st.dataframe(top_skills_df, use_container_width=True)
        else:
            st.info("Không có dữ liệu kỹ năng phù hợp với bộ lọc hiện tại.")

    # ==========================================
    # TAB 3: MỨC LƯƠNG & KINH NGHIỆM
    # ==========================================
    with tab3:
        st.subheader("Phân Tích Mức Lương Theo Vị Trí & Cấp Bậc")

        salary_df = filtered_df.dropna(subset=["salary_avg"])
        SENIORITY_ORDER = ["Fresher / Intern", "Junior (1-2 năm)", "Middle (3-5 năm)", "Senior / Lead (>5 năm)"]

        if not salary_df.empty:
            # Tóm tắt các chỉ số nổi bật
            s_avg = round(salary_df["salary_avg"].mean(), 1)
            s_min = round(salary_df["salary_min"].dropna().mean(), 1) if not salary_df["salary_min"].dropna().empty else 0.0
            s_max = round(salary_df["salary_max"].dropna().mean(), 1) if not salary_df["salary_max"].dropna().empty else 0.0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Lương TB Toàn Ngành", f"{s_avg} tr VNĐ")
            m2.metric("Lương Min Trung Bình", f"{s_min} tr VNĐ")
            m3.metric("Lương Max Trung Bình", f"{s_max} tr VNĐ")
            m4.metric("Số Vị Trí Phân Tích", f"{salary_df['role_category'].nunique()} nhóm vai trò")

            st.markdown("---")

            c1, c2 = st.columns([1.1, 0.9])
            with c1:
                st.markdown("#### 1. Dải Lương Theo Cấp Bậc Kinh Nghiệm")
                view_mode = st.radio(
                    "Chế độ hiển thị dải lương:",
                    ["Cột Nhóm (Min - TB - Max) — Trực quan, dễ xem", "Biểu Đồ Hộp (Box Plot) — Phân tán thống kê"],
                    horizontal=True,
                    label_visibility="collapsed"
                )

                if "Cột Nhóm" in view_mode:
                    sen_agg = salary_df.groupby("seniority_level").agg(
                        luong_min=("salary_min", "mean"),
                        luong_avg=("salary_avg", "mean"),
                        luong_max=("salary_max", "mean")
                    ).reindex(SENIORITY_ORDER).dropna(how="all").round(1).reset_index()

                    melted = pd.melt(
                        sen_agg,
                        id_vars=["seniority_level"],
                        value_vars=["luong_min", "luong_avg", "luong_max"],
                        var_name="loai_luong",
                        value_name="muc_luong"
                    )
                    mapping = {
                        "luong_min": "Lương Tối Thiểu (Min)",
                        "luong_avg": "Lương Trung Bình (Avg)",
                        "luong_max": "Lương Tối Đa (Max)"
                    }
                    melted["loai_luong"] = melted["loai_luong"].map(mapping)

                    fig_bar = px.bar(
                        melted,
                        x="seniority_level",
                        y="muc_luong",
                        color="loai_luong",
                        barmode="group",
                        text_auto=".1f",
                        labels={"seniority_level": "Cấp bậc", "muc_luong": "Mức lương (Triệu VNĐ)", "loai_luong": "Chỉ số"},
                        category_orders={"seniority_level": SENIORITY_ORDER},
                        color_discrete_map={
                            "Lương Tối Thiểu (Min)": "#93C5FD",
                            "Lương Trung Bình (Avg)": "#2563EB",
                            "Lương Tối Đa (Max)": "#1E3A8A"
                        }
                    )
                    fig_bar.update_traces(textposition="outside", texttemplate="%{y:.1f} tr")
                    fig_bar.update_layout(
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        margin=dict(t=40, b=0, l=0, r=0),
                        yaxis_title="Triệu VNĐ",
                        xaxis_title=""
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    fig_box = px.box(
                        salary_df,
                        x="seniority_level",
                        y="salary_avg",
                        color="seniority_level",
                        category_orders={"seniority_level": SENIORITY_ORDER},
                        labels={"seniority_level": "Cấp bậc", "salary_avg": "Mức lương (Triệu VNĐ)"},
                        color_discrete_sequence=["#93C5FD", "#60A5FA", "#2563EB", "#1E3A8A"]
                    )
                    fig_box.update_traces(boxmean=True)
                    fig_box.update_layout(
                        showlegend=False,
                        margin=dict(t=40, b=0, l=0, r=0),
                        xaxis_title=""
                    )
                    st.plotly_chart(fig_box, use_container_width=True)

            with c2:
                st.markdown("#### 2. Lương Trung Bình Theo Vai Trò Chuyên Môn")
                role_sal = salary_df.groupby("role_category")["salary_avg"].mean().round(1).reset_index()
                role_sal = role_sal.sort_values(by="salary_avg", ascending=True)
                fig_bar_sal = px.bar(
                    role_sal, x="salary_avg", y="role_category", orientation="h",
                    color="salary_avg", color_continuous_scale="Blues",
                    text="salary_avg",
                    labels={"salary_avg": "Lương TB (Triệu VNĐ)", "role_category": "Vị trí"}
                )
                fig_bar_sal.update_traces(textposition="outside", texttemplate="%{x:.1f} tr")
                fig_bar_sal.update_layout(
                    margin=dict(t=40, b=0, l=0, r=0),
                    xaxis_title="Triệu VNĐ",
                    yaxis_title="",
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_bar_sal, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 3. Ma Trận Nhiệt Mức Lương: Vị Trí Chuyên Môn × Cấp Bậc Kinh Nghiệm (Triệu VNĐ)")
            st.caption("💡 Biểu đồ Heatmap 2 chiều kết nối trực quan giữa Vị trí IT và Cấp bậc kinh nghiệm, hiển thị cụ thể mức lương trung bình kỳ vọng.")

            pivot = salary_df.pivot_table(index="role_category", columns="seniority_level", values="salary_avg", aggfunc="mean")
            valid_cols = [c for c in SENIORITY_ORDER if c in pivot.columns]
            pivot = pivot.reindex(columns=valid_cols).round(1)
            text_matrix = pivot.map(lambda v: f"{v:.1f} tr" if pd.notnull(v) else "—")

            fig_heat = px.imshow(
                pivot,
                color_continuous_scale="Blues",
                aspect="auto",
                labels=dict(x="Cấp bậc kinh nghiệm", y="Vị trí chuyên môn", color="Lương TB (Triệu VNĐ)")
            )
            fig_heat.update_traces(text=text_matrix, texttemplate="%{text}")
            fig_heat.update_layout(margin=dict(t=20, b=10, l=0, r=0))
            st.plotly_chart(fig_heat, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 4. Top Kỹ Năng Đem Lại Thu Nhập Cao Nhất Thị Trường")
            mart_skills_sal = load_mart("skills_salary")
            if not mart_skills_sal.empty:
                fig_high_pay = px.bar(
                    mart_skills_sal.head(12), x="skill", y="salary_avg",
                    color="salary_avg", color_continuous_scale="Teal",
                    text="salary_avg",
                    labels={"skill": "Công nghệ / Kỹ năng", "salary_avg": "Lương TB (Triệu VNĐ)"}
                )
                fig_high_pay.update_traces(textposition="outside", texttemplate="%{y:.1f} tr")
                fig_high_pay.update_layout(
                    margin=dict(t=30, b=0, l=0, r=0),
                    yaxis_title="Triệu VNĐ",
                    xaxis_title="",
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_high_pay, use_container_width=True)
        else:
            st.info("Chưa có đủ số liệu lương để phân tích cho bộ lọc này.")

    # ==========================================
    # TAB 4: KHÁM PHÁ DỮ LIỆU
    # ==========================================
    with tab4:
        st.subheader("Bảng Dữ Liệu Tuyển Dụng Chi Tiết")
        search_kw = st.text_input("Nhập từ khóa tìm kiếm (Tiêu đề, Công ty, Kỹ năng):", "")
        display_df = filtered_df.copy()

        if search_kw:
            mask = (
                display_df["job_title"].str.contains(search_kw, case=False, na=False) |
                display_df["company_name"].str.contains(search_kw, case=False, na=False) |
                display_df["skills_str"].str.contains(search_kw, case=False, na=False)
            )
            display_df = display_df[mask]

        cols_to_show = ["job_title", "company_name", "location_standard", "salary_raw", "salary_avg", "seniority_level", "skills_str", "job_url"]
        st.dataframe(display_df[cols_to_show], use_container_width=True)

        csv_download = display_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 Tải tập dữ liệu lọc hiện tại (.CSV)",
            data=csv_download,
            file_name="vietnam_it_jobs_filtered.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
