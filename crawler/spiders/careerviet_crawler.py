"""
Crawler chuyên biệt cho CareerViet.vn (CareerBuilder Việt Nam)
Ngành: Công nghệ thông tin / Phần mềm / Developer
Áp dụng bộ lọc Exclusion Filter (Chương 1.3 Đề Cương) loại bỏ tin phi-CNTT
"""

import re
import sys
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Đảm bảo UTF-8 cho Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Các từ khóa không thuộc IT cần loại trừ (Theo Chương 1.3 Đề cương)
NON_IT_KEYWORDS = [
    "kế toán", "c&b", "sản xuất", "lái xe", "công nhân", "thu ngân", "phục vụ",
    "bảo vệ", "bếp", "bất động sản", "line lead", "ca sản xuất", "tạp vụ",
    "kinh doanh nhà hàng", "giao hàng", "shipper", "thợ hàn", "thợ may"
]

# Các từ khóa đặc trưng CNTT
IT_MUST_KEYWORDS = [
    "it", "developer", "engineer", "software", "programmer", "lập trình",
    "backend", "frontend", "fullstack", "devops", "cloud", "data", "ai",
    "qa", "qc", "tester", "java", "python", "golang", ".net", "c#", "c++",
    "react", "node", "php", "mobile", "ios", "android", "system", "network",
    "security", "an toàn thông tin", "chuyên viên công nghệ", "quản trị mạng"
]

class CareerVietCrawler:
    BASE_URL = "https://careerviet.vn"
    SEARCH_ENDPOINTS = [
        "https://careerviet.vn/viec-lam/it-k-vi.html",
        "https://careerviet.vn/viec-lam/developer-k-vi.html",
        "https://careerviet.vn/vi/tim-viec-lam/it-phan-mem.35b7.html"
    ]

    def __init__(self, headers=None, delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
            "Referer": "https://careerviet.vn/"
        }
        self.session.headers.update(self.headers)

    def generate_job_id(self, job_url, title, company):
        raw_key = f"{job_url}|{title}|{company}".lower().strip()
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def is_it_job(self, title, description=""):
        """Bộ lọc kiểm định tin tuyển dụng có thuộc ngành CNTT hay không (Chương 1.3)"""
        text = f"{title} {description}".lower()
        # 1. Nếu dính từ khóa cấm -> loại bỏ ngay
        if any(non_it in text for non_it in NON_IT_KEYWORDS):
            return False
        # 2. Nếu có từ khóa CNTT -> chấp nhận
        if any(re.search(rf"\b{re.escape(k)}\b", text) for k in IT_MUST_KEYWORDS):
            return True
        return False

    def crawl_endpoint(self, url):
        print(f"[CareerVietCrawler] Đang quét: {url}")
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"[CareerVietCrawler] HTTP {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".job-item, figure")
            jobs = []

            for card in cards:
                job_data = self._parse_card(card)
                if job_data:
                    jobs.append(job_data)

            print(f"[CareerVietCrawler] Thu được {len(jobs)} tin CNTT hợp lệ từ {url}")
            return jobs
        except Exception as e:
            print(f"[CareerVietCrawler] Lỗi: {e}")
            return []

    def _parse_card(self, card):
        try:
            title_el = card.select_one(".title a, a.job_link, a.job-title")
            if not title_el:
                return None

            job_title = title_el.get_text(strip=True).replace("(Mới)", "").strip()
            href = title_el.get("href", "")
            job_url = urljoin(self.BASE_URL, href)

            comp_el = card.select_one(".caption a, a.company-name, .employer-name, p.company-name, [class*='company'] a")
            company_name = comp_el.get_text(strip=True) if comp_el else "Doanh nghiệp Công nghệ"

            sal_el = card.select_one(".salary, .job-salary, .wage, [class*='salary']")
            salary_raw = sal_el.get_text(strip=True).replace("Lương:", "").strip() if sal_el else "Thỏa thuận"

            loc_el = card.select_one(".location, .job-location, .city, [class*='location']")
            location = loc_el.get_text(strip=True) if loc_el else "Hà Nội / TP.HCM"

            date_el = card.select_one(".date, [class*='date'], [class*='time']")
            date_raw = date_el.get_text(strip=True) if date_el else ""
            date_posted = datetime.now().strftime("%Y-%m-%d")
            match_date = re.search(r"\d{2}-\d{2}-\d{4}", date_raw)
            if match_date:
                try:
                    d_obj = datetime.strptime(match_date.group(0), "%d-%m-%Y")
                    date_posted = d_obj.strftime("%Y-%m-%d")
                except Exception:
                    pass

            desc = f"{job_title} tại {company_name}, địa điểm {location}. Mức lương: {salary_raw}."

            # Kiểm tra bộ lọc ngành CNTT
            if not self.is_it_job(job_title, desc):
                return None

            job_id = self.generate_job_id(job_url, job_title, company_name)
            return {
                "job_id": f"cv_{job_id[:12]}",
                "job_title": job_title,
                "company_name": company_name,
                "location": location,
                "salary_raw": salary_raw,
                "experience_req": "1-3 năm",
                "skills_raw": [],
                "date_posted": date_posted,
                "job_url": job_url,
                "job_description": desc,
                "source": "CareerViet"
            }
        except Exception:
            return None

    def crawl_all(self):
        all_jobs = []
        for endpoint in self.SEARCH_ENDPOINTS:
            jobs = self.crawl_endpoint(endpoint)
            all_jobs.extend(jobs)
            time.sleep(self.delay)
        return all_jobs

    def crawl_multiple_pages(self, total_pages=3):
        return self.crawl_all()
