"""
Glints Vietnam Crawler – Thu thập tin tuyển dụng IT từ glints.com/vn
Sử dụng dữ liệu JSON nhúng trong thẻ __NEXT_DATA__ (Next.js SSR)
"""

import sys
import re
import time
import random
import hashlib
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(CURRENT_DIR))
from crawler.config import DEFAULT_HEADERS

GLINTS_URL = "https://glints.com/vn/opportunities/jobs/explore?country=VN&industry=7"

IT_KEYWORDS = [
    "engineer", "developer", "programmer", "devops", "data", "backend", "frontend",
    "fullstack", "mobile", "cloud", "qa", "qc", "tester", "ai", "machine learning",
    "software", "architect", "ios", "android", "python", "java", "php", "golang",
    "node", "react", "angular", "vue", "net", "tech", "digital", "it ", "information"
]

class GlintsVNCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            **DEFAULT_HEADERS,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def _is_it_job(self, title: str) -> bool:
        t = title.lower()
        return any(kw in t for kw in IT_KEYWORDS)

    def _format_salary(self, salaries: list) -> str:
        """Chuyển Glints salary array → chuỗi thân thiện"""
        if not salaries:
            return "Thỏa thuận"
        try:
            s = salaries[0]
            min_s = s.get("minAmount", 0)
            max_s = s.get("maxAmount", 0)
            currency = s.get("currency", "VND")
            if not min_s and not max_s:
                return "Thỏa thuận"
            if currency == "VND":
                return f"{int(min_s/1_000_000)} - {int(max_s/1_000_000)} triệu"
            else:
                return f"{min_s} - {max_s} {currency}"
        except Exception:
            return "Thỏa thuận"

    def _format_exp(self, min_exp, max_exp) -> str:
        if min_exp is None:
            return "Không yêu cầu"
        if max_exp:
            return f"{min_exp}-{max_exp} năm"
        return f"{min_exp}+ năm"

    def crawl_page(self, page_num: int = 1) -> list:
        # Glints pagination uses ?page=N (1-indexed)
        if page_num == 1:
            url = "https://glints.com/vn/opportunities/jobs/explore?country=VN&industry=7"
        else:
            url = f"https://glints.com/vn/opportunities/jobs/explore?country=VN&industry=7&page={page_num}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"[GlintsVNCrawler] Lỗi khi tải trang {page_num}: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract __NEXT_DATA__ JSON (Next.js Server Side Rendering)
        # Use find() with id= kwarg which reliably locates the script tag
        next_data_tag = soup.find("script", {"id": "__NEXT_DATA__"})
        if not next_data_tag or not next_data_tag.string:
            print(f"[GlintsVNCrawler] Không tìm thấy __NEXT_DATA__ ở trang {page_num} (có thể bị chặn hoặc thay đổi cấu trúc)")
            return []

        try:
            next_data = json.loads(next_data_tag.string)
            page_props = next_data.get("props", {}).get("pageProps", {})
            initial_jobs = page_props.get("initialJobs", {})
            raw_jobs = initial_jobs.get("jobsInPage", []) if isinstance(initial_jobs, dict) else []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"[GlintsVNCrawler] Parse lỗi: {e}")
            return []

        results = []
        for j in raw_jobs:
            try:
                title = j.get("title", "")
                if not title or not self._is_it_job(title):
                    continue

                company_obj = j.get("company") or {}
                company = company_obj.get("name", "Unknown") if isinstance(company_obj, dict) else "Unknown"

                city_obj = j.get("city") or {}
                location = city_obj.get("name", "Hồ Chí Minh") if isinstance(city_obj, dict) else "Hồ Chí Minh"
                if not location:
                    location = "Hồ Chí Minh"

                salaries = j.get("salaries") or []
                salary_str = self._format_salary(salaries)

                skills_raw = j.get("skills") or []
                skills = [s.get("name", "") for s in skills_raw if isinstance(s, dict) and s.get("name")]

                min_exp = j.get("minYearsOfExperience")
                max_exp = j.get("maxYearsOfExperience")
                exp_str = self._format_exp(min_exp, max_exp)

                created_at = j.get("createdAt", "")
                try:
                    date_posted = datetime.fromisoformat(created_at[:10]).strftime("%Y-%m-%d")
                except Exception:
                    date_posted = datetime.now().strftime("%Y-%m-%d")

                job_id_raw = str(j.get("id", "")) + title + company
                job_id = "glints_" + hashlib.md5(job_id_raw.encode()).hexdigest()[:10]

                results.append({
                    "job_id": job_id,
                    "job_title": title,
                    "company_name": company,
                    "location": location,
                    "salary_raw": salary_str,
                    "experience_req": exp_str,
                    "skills_raw": skills,
                    "date_posted": date_posted,
                    "job_url": f"https://glints.com/vn/opportunities/jobs/{j.get('id', '')}",
                    "job_description": f"{title} tại {company} ({location}). Kỹ năng: {', '.join(skills) if skills else 'Xem chi tiết'}. Lương: {salary_str}.",
                    "source": "Glints Vietnam"
                })

            except Exception:
                continue

        print(f"[GlintsVNCrawler] Trang {page_num}: Thu được {len(results)} tin IT từ {url}")
        return results

    def crawl_multiple_pages(self, total_pages: int = 3) -> list:
        all_jobs = []
        for page in range(1, total_pages + 1):
            jobs = self.crawl_page(page)
            all_jobs.extend(jobs)
            if page < total_pages:
                time.sleep(random.uniform(1.5, 2.5))
        return all_jobs


if __name__ == "__main__":
    crawler = GlintsVNCrawler()
    jobs = crawler.crawl_multiple_pages(total_pages=2)
    print(f"Tổng: {len(jobs)} tin từ Glints VN")
    if jobs:
        print(json.dumps(jobs[0], ensure_ascii=False, indent=2))
