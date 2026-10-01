"""
ITviec Crawler – Thu thập tin tuyển dụng IT từ itviec.com
Phân tích HTML trực tiếp từ job-card divs (20 job/page)
"""

import sys
import re
import time
import random
import hashlib
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(CURRENT_DIR))
from crawler.config import DEFAULT_HEADERS

ITVIEC_BASE_URL = "https://itviec.com"
ITVIEC_IT_URL   = "https://itviec.com/it-jobs"

IT_KEYWORDS = [
    "engineer", "developer", "programmer", "devops", "data", "backend", "frontend",
    "fullstack", "mobile", "cloud", "qa", "qc", "tester", "ai", "machine learning",
    "software", "architect", "sre", "security", "embedded", "ios", "android", "python",
    "java", "php", "golang", "node", "react", "angular", "vue", "net", "scala"
]

class ITviecCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _is_it_job(self, title: str) -> bool:
        # ITviec is an IT-only board – accept all jobs (no filtering needed)
        return True

    def _parse_date(self, raw: str) -> str:
        """Parse 'Posted X minutes/hours/days ago' → YYYY-MM-DD"""
        raw = raw.lower().strip()
        today = datetime.now()
        if "minute" in raw or "just now" in raw or "hour" in raw:
            return today.strftime("%Y-%m-%d")
        m = re.search(r"(\d+)\s*day", raw)
        if m:
            from datetime import timedelta
            return (today - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")
        return today.strftime("%Y-%m-%d")

    def crawl_page(self, page_num: int = 1) -> list:
        url = ITVIEC_IT_URL if page_num == 1 else f"{ITVIEC_IT_URL}?page={page_num}"
        try:
            resp = self.session.get(url, timeout=12)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ITviecCrawler] Lỗi khi tải trang {page_num}: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        job_cards = soup.select("div.job-card")
        results = []

        for card in job_cards:
            try:
                # Title + URL
                title_tag = card.select_one("h3 a, h2 a")
                title = title_tag.get_text(strip=True) if title_tag else ""
                job_url = title_tag.get("href", "") if title_tag else ""
                if not job_url.startswith("http"):
                    job_url = ITVIEC_BASE_URL + job_url

                if not title:
                    continue

                # Company: find anchor with /companies/ and non-empty text
                company = "Unknown"
                for a in card.select("a"):
                    if "/companies/" in a.get("href", ""):
                        txt = a.get_text(strip=True)
                        if txt:
                            company = txt
                            break

                # Salary
                salary = "Thỏa thuận"
                for el in card.select("span[class*='salary'], div[class*='salary']"):
                    sal_text = el.get_text(strip=True)
                    if sal_text and "sign in" not in sal_text.lower():
                        salary = sal_text
                        break

                # Location: look for spans after SVG or known city keywords
                location = "Hà Nội"
                for sp in card.select("span"):
                    txt = sp.get_text(strip=True)
                    if any(city in txt for city in ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Da Nang", "Hanoi", "Ho Chi Minh", "HCM", "Remote"]):
                        location = txt
                        break

                # Posted date
                date_tag = card.select_one("span.small-text")
                date_posted = self._parse_date(date_tag.get_text() if date_tag else "")

                # Skills: anchor tags with class containing 'itag' or 'tag'
                skill_tags = card.select("a.itag, a[class*='itag'], a.tag--job-skill, span.tag")
                skills = [s.get_text(strip=True) for s in skill_tags if s.get_text(strip=True) and len(s.get_text(strip=True)) < 40]

                # Experience
                exp_tag = card.select_one("div[class*=exp], span[class*=exp], li[class*=exp]")
                exp_raw = exp_tag.get_text(strip=True) if exp_tag else ""

                # Generate unique job_id
                job_id = "itviec_" + hashlib.md5(f"{title}{company}{date_posted}".encode()).hexdigest()[:10]

                results.append({
                    "job_id": job_id,
                    "job_title": title,
                    "company_name": company,
                    "location": location,
                    "salary_raw": salary,
                    "experience_req": exp_raw or "Không yêu cầu",
                    "skills_raw": skills,
                    "date_posted": date_posted,
                    "job_url": job_url,
                    "job_description": f"{title} tại {company} ({location}). Kỹ năng yêu cầu: {', '.join(skills) if skills else 'Xem chi tiết'}.",
                    "source": "ITviec"
                })

            except Exception:
                continue

        print(f"[ITviecCrawler] Trang {page_num}: Thu được {len(results)} tin IT từ {url}")
        return results

    def crawl_multiple_pages(self, total_pages: int = 3) -> list:
        all_jobs = []
        for page in range(1, total_pages + 1):
            jobs = self.crawl_page(page)
            all_jobs.extend(jobs)
            if page < total_pages:
                time.sleep(random.uniform(1.5, 3.0))
        return all_jobs


if __name__ == "__main__":
    crawler = ITviecCrawler()
    jobs = crawler.crawl_multiple_pages(total_pages=2)
    print(f"Tổng: {len(jobs)} tin từ ITviec")
    if jobs:
        import json
        print(json.dumps(jobs[0], ensure_ascii=False, indent=2))
