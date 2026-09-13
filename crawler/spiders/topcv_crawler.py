"""
Crawler chuyên biệt cho TopCV.vn
Ngành: Việc làm IT / Phần mềm
Trang gốc: https://www.topcv.vn/tim-viec-lam-it-phan-mem-c10026
"""

import re
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

class TopCVCrawler:
    BASE_URL = "https://www.topcv.vn"
    LIST_URL = "https://www.topcv.vn/tim-viec-lam-it-phan-mem-c10026"
    PAGE_URL_TEMPLATE = "https://www.topcv.vn/tim-viec-lam-it-phan-mem-c10026?page={page}"

    def __init__(self, headers=None, delay=2.0):
        self.delay = delay
        self.session = requests.Session()
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.topcv.vn/"
        }
        self.session.headers.update(self.headers)

    def generate_job_id(self, job_url, title, company):
        raw_key = f"{job_url}|{title}|{company}".lower().strip()
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def crawl_page(self, page_num=1):
        url = self.LIST_URL if page_num == 1 else self.PAGE_URL_TEMPLATE.format(page=page_num)
        print(f"[TopCVCrawler] Đang tải trang {page_num}: {url}")
        
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"[TopCVCrawler] Thông báo: Server trả về mã {resp.status_code} (Có thể có bảo vệ WAF/Cloudflare)")
                return []
            
            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = []
            
            # Khối việc làm trên TopCV
            job_cards = soup.select(".job-item-search-result, .job-item, .job-ta, div[data-box='box-search-job']")
            
            for card in job_cards:
                job_data = self._parse_card(card)
                if job_data:
                    jobs.append(job_data)

            print(f"[TopCVCrawler] Thu thập được {len(jobs)} việc làm từ TopCV trang {page_num}")
            return jobs
        except Exception as e:
            print(f"[TopCVCrawler] Lỗi kết nối TopCV: {e}")
            return []

    def _parse_card(self, card):
        try:
            title_tag = card.select_one("h3.title a, .job-title a, a[class*='title']")
            if not title_tag:
                return None
            
            job_title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            job_url = urljoin(self.BASE_URL, href)

            company_tag = card.select_one("a.company, .company-name, [class*='company'] a")
            company_name = company_tag.get_text(strip=True) if company_tag else "Công ty Công nghệ"

            salary_tag = card.select_one(".salary, [class*='salary'], span.text-salary")
            salary_raw = salary_tag.get_text(strip=True) if salary_tag else "Thỏa thuận"

            location_tag = card.select_one(".address, [class*='address'], [class*='city'], .location")
            location = location_tag.get_text(strip=True) if location_tag else "Hà Nội"

            exp_tag = card.select_one(".exp, [class*='exp']")
            experience_req = exp_tag.get_text(strip=True) if exp_tag else "1 năm"

            skills_raw = []
            tag_elements = card.select(".badge, .tag, [class*='tag'], [class*='skill']")
            for t in tag_elements:
                txt = t.get_text(strip=True)
                if txt and len(txt) < 30:
                    skills_raw.append(txt)

            job_id = self.generate_job_id(job_url, job_title, company_name)
            return {
                "job_id": f"topcv_{job_id[:12]}",
                "job_title": job_title,
                "company_name": company_name,
                "location": location,
                "salary_raw": salary_raw,
                "experience_req": experience_req,
                "skills_raw": skills_raw,
                "date_posted": datetime.now().strftime("%Y-%m-%d"),
                "job_url": job_url,
                "job_description": f"{job_title} tại {company_name}. Lương: {salary_raw}. Địa điểm: {location}",
                "source": "TopCV"
            }
        except Exception:
            return None

    def crawl_multiple_pages(self, total_pages=2):
        all_jobs = []
        for p in range(1, total_pages + 1):
            page_jobs = self.crawl_page(p)
            all_jobs.extend(page_jobs)
            if p < total_pages:
                time.sleep(self.delay)
        return all_jobs
