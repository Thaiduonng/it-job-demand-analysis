import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
MARTS_DATA_DIR = os.path.join(DATA_DIR, "marts")

# Ensure directories exist
for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MARTS_DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# Default headers to mimic real desktop browsers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1"
}

# Target Job Boards
URLS = {
    "careerviet_it": "https://careerviet.vn/vi/tim-viec-lam/it-phan-mem.35b7.html",
    "topcv_it": "https://www.topcv.vn/tim-viec-lam-it-phan-mem-c10026",
}

# Key IT Domains / Keywords
IT_KEYWORDS = [
    "java", "python", "golang", "c#", ".net", "php", "javascript", "typescript",
    "react", "vue", "angular", "node", "spring boot", "django", "fastapi",
    "backend", "frontend", "fullstack", "devops", "cloud", "aws", "azure", "gcp",
    "data engineer", "data analyst", "data scientist", "machine learning", "ai",
    "tester", "qa", "qc", "embedded", "mobile", "ios", "android", "flutter"
]
