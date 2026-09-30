"""
Apache Spark Cluster Job - Phân Tích Nhu Cầu Tuyển Dụng CNTT
Chạy phân tán trực tiếp trên Spark Master & Spark Worker (Cluster Mode)
Đọc dữ liệu từ Hadoop HDFS: hdfs://namenode:9000/data/processed/jobs_cleaned.parquet
"""

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg

def main():
    # Khởi tạo Spark Session kết nối vào cụm Spark Master
    spark = SparkSession.builder \
        .appName("VietnamITRecruitmentAnalytics") \
        .master("spark://spark-master:7077") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.cores.max", "2") \
        .getOrCreate()

    print("=" * 60)
    print("SPARK CLUSTER APPLICATION: VietnamITRecruitmentAnalytics")
    print("Master Cluster URL:", spark.sparkContext.master)
    print("Application ID:", spark.sparkContext.applicationId)
    print("=" * 60)

    # Đọc dữ liệu từ HDFS
    hdfs_url = "hdfs://namenode:9000/data/processed/jobs_cleaned.parquet"
    print(f"[Spark Read] Đang nạp dữ liệu từ Hadoop HDFS: {hdfs_url} ...")
    
    try:
        df = spark.read.parquet(hdfs_url)
    except Exception as e:
        print(f"[Cảnh báo] Đọc fallback từ volume /spark/data: {e}")
        df = spark.read.parquet("/spark/data/processed/jobs_cleaned.parquet")

    total_records = df.count()
    print(f"\n[HDFS Processed Zone] Tổng số bản tin tuyển dụng: {total_records} tin")

    # Phân tích 1: Top vị trí tuyển dụng
    print("\n--- PHÂN TÍCH 1: TOP VỊ TRÍ TUYỂN DỤNG IT TRÊN CỤM SPARK ---")
    df.groupBy("role_category") \
      .agg(count("job_id").alias("so_luong_tin")) \
      .orderBy(col("so_luong_tin").desc()) \
      .show(10, truncate=False)

    # Phân tích 2: Lương trung bình theo vị trí
    print("\n--- PHÂN TÍCH 2: MỨC LƯƠNG TRUNG BÌNH THEO VỊ TRÍ (TRIỆU VNĐ) ---")
    df.filter(col("salary_avg").isNotNull()) \
      .groupBy("role_category") \
      .agg(avg("salary_avg").alias("luong_trung_binh"), count("job_id").alias("so_tin")) \
      .orderBy(col("luong_trung_binh").desc()) \
      .show(10, truncate=False)

    # Phân tích 3: Phân bố việc làm theo thành phố
    print("\n--- PHÂN TÍCH 3: PHÂN BỐ VIỆC LÀM THEO KHU VỰC ĐỊA LÝ ---")
    df.groupBy("location_standard") \
      .agg(count("job_id").alias("so_luong_tin")) \
      .orderBy(col("so_luong_tin").desc()) \
      .show(10, truncate=False)

    print("=" * 60)
    print("TÁC VỤ PHÂN TÍCH SPARK CLUSTER HOÀN TẤT THÀNH CÔNG!")
    print("=" * 60)

    spark.stop()

if __name__ == "__main__":
    main()
