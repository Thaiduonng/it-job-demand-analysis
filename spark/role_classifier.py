"""
Module Phân Loại Vị Trí / Vai Trò Công Việc IT (Job Role Classifier)
Phân loại tiêu đề công việc vào các nhóm ngành chuẩn trong thị trường tuyển dụng CNTT:
- Backend Developer
- Frontend Developer
- Fullstack Developer
- Mobile Developer
- Data Engineer / Big Data
- Data Analyst / BI
- AI / Machine Learning Engineer
- DevOps / Cloud Engineer
- QA / QC / Automation Tester
- Khác / Quản lý dự án
"""

import re

ROLE_PATTERNS = {
    "Data Engineer / Big Data": [
        r"\bdata\s*engineer\b", r"\bbig\s*data\b", r"\bdata\s*pipeline\b", r"\betl\b",
        r"\bspark\b", r"\bhadoop\b"
    ],
    "Data Analyst / BI": [
        r"\bdata\s*analyst\b", r"\bbi\s*developer\b", r"\bbusiness\s*intelligence\b",
        r"\bdata\s*analytics\b"
    ],
    "AI / Machine Learning Engineer": [
        r"\bmachine\s*learning\b", r"\bai\s*engineer\b", r"\bdata\s*scientist\b",
        r"\bdeep\s*learning\b", r"\bnlp\b", r"\bcomputer\s*vision\b"
    ],
    "Backend Developer": [
        r"\bbackend\b", r"\bback-end\b", r"\bjava\b", r"\bgolang\b", r"\bpython\b(?=.*dev|.*engineer)",
        r"\bphp\b", r"\b\.net\b", r"\bc#\b", r"\bnodejs\b", r"\bspring\b"
    ],
    "Frontend Developer": [
        r"\bfrontend\b", r"\bfront-end\b", r"\breact\b", r"\bvue\b", r"\bangular\b",
        r"\bui/ux\b", r"\bweb\s*developer\b"
    ],
    "Fullstack Developer": [
        r"\bfullstack\b", r"\bfull-stack\b", r"\bfull\s*stack\b"
    ],
    "Mobile Developer": [
        r"\bmobile\b", r"\bios\b", r"\bandroid\b", r"\bflutter\b", r"\breact\s*native\b"
    ],
    "DevOps / Cloud Engineer": [
        r"\bdevops\b", r"\bcloud\b", r"\bsre\b", r"\bsystem\s*admin\b", r"\binfrastructure\b",
        r"\bkubernetes\b", r"\baws\b(?=.*engineer|.*architect)"
    ],
    "QA / QC / Automation Tester": [
        r"\bqa\b", r"\bqc\b", r"\btester\b", r"\btesting\b", r"\bautomation\s*test\b",
        r"\bquality\s*assurance\b"
    ]
}

COMPILED_ROLE_PATTERNS = {
    role: [re.compile(p, re.IGNORECASE) for p in patterns]
    for role, patterns in ROLE_PATTERNS.items()
}

def classify_job_role(title, description=""):
    """
    Xác định vai trò chuyên môn dựa trên tiêu đề công việc và mô tả tóm tắt
    """
    if not title or not isinstance(title, str):
        return "IT Chuyên môn khác"

    title_lower = title.lower()

    # Ưu tiên tìm trong Tiêu đề bài đăng trước
    for role, patterns in COMPILED_ROLE_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(title_lower):
                return role

    # Nếu tiêu đề quá chung chung (vd: Software Engineer), phân tích thêm mô tả
    if description and isinstance(description, str):
        desc_lower = description.lower()
        for role, patterns in COMPILED_ROLE_PATTERNS.items():
            for pattern in patterns:
                if pattern.search(desc_lower):
                    return role

    return "Software Engineer (Chung)"
