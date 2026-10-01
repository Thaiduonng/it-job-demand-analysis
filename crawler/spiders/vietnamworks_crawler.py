"""
VietnamWorks Crawler – Thu thập tin tuyển dụng IT từ vietnamworks.com
Sử dụng VietnamWorks Public Job Search API (v3)
"""

import sys
import re
import time
import random
import hashlib
import json
import requests
from datetime import datetime
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(CURRENT_DIR))
from crawler.config import DEFAULT_HEADERS

# VietnamWorks Job Search API (không cần xác thực)
VW_SEARCH_API = "https://ms.vietnamworks.com/job-search/v1.0/search"

# Category IDs cho IT/Phần mềm trên VietnamWorks
IT_CATEGORY_IDS = [35, 178, 179, 180, 181, 182, 183]  # IT Software & Hardware categories

VW_HEADERS = {
    **DEFAULT_HEADERS,
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://www.vietnamworks.com",
    "Referer": "https://www.vietnamworks.com/",
}

class VietnamWorksCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(VW_HEADERS)

    def _format_salary(self, min_sal: float, max_sal: float, currency: str) -> str:
        if not min_sal and not max_sal:
            return "Thỏa thuận"
        if currency == "USD":
            return f"{int(min_sal)} - {int(max_sal)} USD"
        elif currency in ("VND", "VNĐ"):
            return f"{int(min_sal/1_000_000)} - {int(max_sal/1_000_000)} triệu"
        return f"{min_sal} - {max_sal} {currency}"

    def _format_exp(self, years_exp: str) -> str:
        if not years_exp:
            return "Không yêu cầu"
        return str(years_exp)

    def crawl_page(self, query: str = "developer", page_num: int = 0, page_size: int = 20) -> list:
        """
        VietnamWorks API pagination: page bắt đầu từ 0.
        Response: {'data': [list of jobs], 'meta': {...}, 'facets': [...]}
        """
        payload = {
            "query": query,
            "filter": [],
            "ranges": [],
            "order": [],
            "hitsPerPage": page_size,
            "page": page_num,
            "retrieveFields": [
                "jobTitle", "salaryMin", "salaryMax", "isSalaryVisible",
                "alias", "approvedOn", "companyId", "jobLevelVI",
                "skills", "workingLocations", "salary", "prettySalary",
                "companyName", "yearsOfExperience", "jobDescription"
            ]
        }
        try:
            resp = self.session.post(VW_SEARCH_API, json=payload, timeout=12)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[VietnamWorksCrawler] Lỗi truy vấn '{query}' trang {page_num}: {e}")
            return []

        # VietnamWorks API: top-level 'data' is a list of job objects
        hits = data.get("data", [])
        if isinstance(hits, dict):
            hits = hits.get("hits", []) or []

        if not hits:
            print(f"[VietnamWorksCrawler] Không tìm thấy kết quả cho '{query}' trang {page_num}")
            return []

        results = []
        for h in hits:
            try:
                title = (h.get("jobTitle") or "").strip()
                if not title:
                    continue

                company = (h.get("companyName") or "Unknown").strip()

                # Location – workingLocations is a list of dicts
                working_locs = h.get("workingLocations") or []
                if working_locs and isinstance(working_locs[0], dict):
                    location = working_locs[0].get("cityNameVI") or working_locs[0].get("cityName") or "Hồ Chí Minh"
                else:
                    location = "Hồ Chí Minh"

                # Salary – prettySalary is human-readable string
                salary = (h.get("prettySalary") or h.get("salary") or "Thỏa thuận")
                if not salary or str(salary) == "0":
                    salary = "Thỏa thuận"

                # Skills – list of dicts with 'skillName'
                skills_raw = h.get("skills") or []
                skills = []
                for s in skills_raw:
                    if isinstance(s, dict):
                        skill_name = s.get("skillName") or s.get("name") or ""
                        if skill_name:
                            skills.append(skill_name.strip())
                    elif isinstance(s, str) and s.strip():
                        skills.append(s.strip())

                # Experience
                years_exp = h.get("yearsOfExperience") or h.get("requiredExp") or ""
                exp = self._format_exp(str(years_exp))

                # Date
                approved_on = h.get("approvedOn", "") or ""
                try:
                    date_posted = datetime.fromisoformat(approved_on[:10]).strftime("%Y-%m-%d")
                except Exception:
                    date_posted = datetime.now().strftime("%Y-%m-%d")

                # URL
                alias = h.get("alias", "") or ""
                job_url = f"https://www.vietnamworks.com/{alias}-jv" if alias else "https://www.vietnamworks.com"

                job_id = "vw_" + hashlib.md5(f"{title}{company}{date_posted}".encode()).hexdigest()[:10]

                results.append({
                    "job_id": job_id,
                    "job_title": title,
                    "company_name": company,
                    "location": location,
                    "salary_raw": str(salary),
                    "experience_req": exp,
                    "skills_raw": skills,
                    "date_posted": date_posted,
                    "job_url": job_url,
                    "job_description": f"{title} tại {company} ({location}). Kỹ năng: {', '.join(skills) if skills else 'Xem JD'}. Lương: {salary}. Kinh nghiệm: {exp}.",
                    "source": "VietnamWorks"
                })

            except Exception:
                continue

        print(f"[VietnamWorksCrawler] '{query}' trang {page_num}: Thu được {len(results)} tin từ API")
        return results

    def crawl_multiple_pages(self, total_pages: int = 3) -> list:
        """
        Crawl theo các từ khóa IT chủ chốt để tối ưu độ phong phú dữ liệu.
        """
        keywords = ["developer", "software engineer", "data engineer", "frontend", "backend", "devops"]
        all_jobs = []
        unique_ids = set()

        for idx, kw in enumerate(keywords[:max(1, total_pages * 2)]):
            page_num = idx % total_pages
            jobs = self.crawl_page(query=kw, page_num=page_num, page_size=20)
            for j in jobs:
                if j["job_id"] not in unique_ids:
                    unique_ids.add(j["job_id"])
                    all_jobs.append(j)
            time.sleep(random.uniform(0.5, 1.2))

        return all_jobs


if __name__ == "__main__":
    crawler = VietnamWorksCrawler()
    jobs = crawler.crawl_multiple_pages(total_pages=2)
    print(f"Tổng: {len(jobs)} tin từ VietnamWorks")
    if jobs:
        print(json.dumps(jobs[0], ensure_ascii=False, indent=2))
