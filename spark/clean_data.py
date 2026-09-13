"""
Module Tiền Xử Lý & Làm Sạch Dữ Liệu Tuyển Dụng (Data Preprocessing & Cleaning)
Hỗ trợ cả PySpark DataFrame và Pandas Fallback Engine.
Thực hiện các nhiệm vụ theo Chương 3.1 & 3.2:
- Khử trùng lặp (Deduplication)
- Chuẩn hóa địa điểm (Location Standardization)
- Phân tích & quy đổi mức lương về đơn vị triệu VND (Salary Standardization)
- Chuẩn hóa số năm kinh nghiệm & Cấp bậc (Experience & Seniority)
"""

import re
import numpy as np

USD_TO_VND_RATE = 25.4  # 1 USD ~ 25,400 VND -> 1,000 USD ~ 25.4 triệu VND

def parse_salary(salary_str):
    """
    Phân tích chuỗi lương (triệu VND, USD, thỏa thuận) về (min_million_vnd, max_million_vnd, avg_million_vnd)
    """
    if not salary_str or not isinstance(salary_str, str) or salary_str.strip().lower() in ["thỏa thuận", "thoa thuan", "negotiable", "cạnh tranh"]:
        return None, None, None

    s = salary_str.lower().replace(",", ".").strip()
    
    # 1. Định dạng USD (vd: 1000 - 2500 usd, 1.500 - 2.000 usd, up to 2000 usd)
    if "usd" in s or "$" in s:
        nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", s.replace(".", ""))]
        if len(nums) >= 2:
            s_min = (nums[0] / 1000.0) * USD_TO_VND_RATE
            s_max = (nums[1] / 1000.0) * USD_TO_VND_RATE
            return round(s_min, 1), round(s_max, 1), round((s_min + s_max) / 2.0, 1)
        elif len(nums) == 1:
            val = (nums[0] / 1000.0) * USD_TO_VND_RATE
            if "tới" in s or "up to" in s or "đến" in s:
                return round(val * 0.7, 1), round(val, 1), round(val * 0.85, 1)
            return round(val, 1), round(val * 1.3, 1), round(val * 1.15, 1)

    # 2. Định dạng Triệu VNĐ (vd: 15 - 25 triệu, 20-35 tr, trên 30 triệu, tới 40tr)
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", s)]
    if len(nums) >= 2:
        s_min = nums[0]
        s_max = nums[1]
        # Xử lý trường hợp viết dạng 15.000.000 - 25.000.000
        if s_min > 1000000:
            s_min /= 1000000.0
        if s_max > 1000000:
            s_max /= 1000000.0
        if s_min > s_max:
            s_min, s_max = s_max, s_min
        return round(s_min, 1), round(s_max, 1), round((s_min + s_max) / 2.0, 1)
    elif len(nums) == 1:
        val = nums[0]
        if val > 1000000:
            val /= 1000000.0
        if "tới" in s or "up to" in s or "đến" in s or "dưới" in s:
            return round(val * 0.7, 1), round(val, 1), round(val * 0.85, 1)
        elif "trên" in s or "từ" in s or "from" in s:
            return round(val, 1), round(val * 1.3, 1), round(val * 1.15, 1)
        return round(val, 1), round(val, 1), round(val, 1)

    return None, None, None

def parse_location(loc_str):
    """
    Chuẩn hóa địa điểm tuyển dụng về các cụm đô thị lớn
    """
    if not loc_str or not isinstance(loc_str, str):
        return "Khác"
    
    loc_lower = loc_str.lower()
    if any(k in loc_lower for k in ["hà nội", "ha noi", "hn"]):
        return "Hà Nội"
    elif any(k in loc_lower for k in ["hồ chí minh", "ho chi minh", "hcm", "sài gòn", "sai gon", "tp.hcm"]):
        return "Hồ Chí Minh"
    elif any(k in loc_lower for k in ["đà nẵng", "da nang", "dn"]):
        return "Đà Nẵng"
    elif any(k in loc_lower for k in ["remote", "toàn quốc", "việt nam", "online"]):
        return "Remote / Toàn quốc"
    else:
        return "Tỉnh thành khác"

def parse_experience(exp_str):
    """
    Trích xuất số năm kinh nghiệm tối thiểu, tối đa và phân loại cấp bậc
    """
    if not exp_str or not isinstance(exp_str, str):
        return 1.0, 3.0, "Junior / Middle"

    exp_lower = exp_str.lower()
    if any(k in exp_lower for k in ["không yêu cầu", "chưa có", "fresher", "intern", "thực tập"]):
        return 0.0, 1.0, "Fresher / Intern"

    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", exp_lower)]
    if len(nums) >= 2:
        exp_min, exp_max = min(nums[0], nums[1]), max(nums[0], nums[1])
    elif len(nums) == 1:
        val = nums[0]
        if "trên" in exp_lower or "hơn" in exp_lower:
            exp_min, exp_max = val, val + 3.0
        elif "dưới" in exp_lower or "tới" in exp_lower:
            exp_min, exp_max = 0.0, val
        else:
            exp_min, exp_max = val, val + 1.0
    else:
        exp_min, exp_max = 1.0, 3.0

    # Phân loại Cấp bậc (Seniority Level)
    if exp_min == 0 and exp_max <= 1:
        seniority = "Fresher / Intern"
    elif exp_max <= 2:
        seniority = "Junior (1-2 năm)"
    elif exp_max <= 5:
        seniority = "Middle (3-5 năm)"
    else:
        seniority = "Senior / Lead (>5 năm)"

    return float(exp_min), float(exp_max), seniority
