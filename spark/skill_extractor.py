"""
Module Trích Xuất Kỹ Năng & Từ Điển Công Nghệ CNTT (IT Skill Extractor)
Sử dụng Regular Expression biên từ (Word Boundary Regex) để bóc tách chính xác
các công nghệ, ngôn ngữ lập trình, framework và database từ mô tả công việc (JD).
"""

import re

# Từ điển ánh xạ công nghệ chuẩn hóa
TECH_TAXONOMY = {
    # Ngôn ngữ lập trình
    "Python": [r"\bpython\b", r"\bpypy\b"],
    "Java": [r"\bjava\b(?!script)", r"\bjvm\b", r"\bj2ee\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b(?!\w)"],
    "TypeScript": [r"\btypescript\b", r"\bts\b(?!\w)"],
    "Golang": [r"\bgolang\b", r"\bgo\s+lang\b", r"\bgo\b(?=\s+developer|\s+backend)"],
    "C# / .NET": [r"\bc#\b", r"\bcsharp\b", r"\b\.net\b", r"\bdot\s*net\b", r"\basp\.net\b"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "PHP": [r"\bphp\b", r"\blaravel\b", r"\bsymfony\b"],
    "Kotlin": [r"\bkotlin\b"],
    "Swift": [r"\bswift\b"],
    "Ruby": [r"\bruby\b", r"\brails\b", r"\bruby\s+on\s+rails\b"],
    "Rust": [r"\brust\b"],
    "Scala": [r"\bscala\b"],
    "SQL": [r"\bsql\b", r"\brdbms\b"],

    # Frontend Frameworks
    "React": [r"\breact\b", r"\breactjs\b", r"\breact\.js\b"],
    "Vue.js": [r"\bvue\b", r"\bvuejs\b", r"\bvue\.js\b"],
    "Angular": [r"\bangular\b", r"\bangularjs\b"],
    "Next.js": [r"\bnextjs\b", r"\bnext\.js\b"],
    "HTML/CSS": [r"\bhtml\b", r"\bcss\b", r"\bhtml5\b", r"\bcss3\b", r"\btailwind\b", r"\bbootstrap\b"],

    # Backend Frameworks
    "Spring Boot": [r"\bspring\s*boot\b", r"\bspring\s*framework\b"],
    "Node.js": [r"\bnode\b", r"\bnodejs\b", r"\bnode\.js\b", r"\bexpress\b", r"\bnestjs\b"],
    "Django / FastAPI": [r"\bdjango\b", r"\bfastapi\b", r"\bflask\b"],

    # Big Data & AI
    "Apache Spark": [r"\bspark\b", r"\bpyspark\b", r"\bapache\s*spark\b"],
    "Hadoop / HDFS": [r"\bhadoop\b", r"\bhdfs\b", r"\bmapreduce\b"],
    "Apache Kafka": [r"\bkafka\b", r"\bapache\s*kafka\b"],
    "Airflow": [r"\bairflow\b", r"\bapache\s*airflow\b"],
    "AI / Machine Learning": [r"\bmachine\s*learning\b", r"\bdeep\s*learning\b", r"\bpytorch\b", r"\btensorflow\b", r"\bnlp\b", r"\bai\b(?=\s+engineer|\s+model)"],
    "Power BI / BI": [r"\bpower\s*bi\b", r"\btableau\b", r"\blooker\b", r"\bdata\s*warehouse\b"],

    # Cloud & DevOps
    "Docker": [r"\bdocker\b", r"\bcontainer\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "AWS": [r"\baws\b", r"\bamazon\s*web\s*services\b"],
    "Azure": [r"\bazure\b", r"\bmicrosoft\s*azure\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle\s*cloud\b"],
    "CI/CD": [r"\bci/cd\b", r"\bjenkins\b", r"\bgitlab\s*ci\b", r"\bgithub\s*actions\b"],
    "Linux": [r"\blinux\b", r"\bubuntu\b", r"\bcentos\b"],

    # Databases
    "MySQL": [r"\bmysql\b"],
    "PostgreSQL": [r"\bpostgres\b", r"\bpostgresql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "Redis": [r"\bredis\b"],
    "Oracle": [r"\boracle\s*db\b", r"\boracle\b(?=\s+database)"],
    "Elasticsearch": [r"\belasticsearch\b", r"\belastic\b"]
}

# Biên dịch trước các Regex để tăng tốc độ xử lý hàng ngàn bản ghi
COMPILED_PATTERNS = {
    skill: [re.compile(p, re.IGNORECASE) for p in patterns]
    for skill, patterns in TECH_TAXONOMY.items()
}

def extract_skills_from_text(text, existing_skills=None):
    """
    Trích xuất danh sách kỹ năng từ văn bản (JD, title, tags)
    """
    found_skills = set()
    if existing_skills and isinstance(existing_skills, list):
        for s in existing_skills:
            if isinstance(s, str) and s.strip():
                # Chuẩn hóa kỹ năng đã có từ tag
                s_clean = s.strip()
                matched = False
                for skill_name, patterns in COMPILED_PATTERNS.items():
                    for pattern in patterns:
                        if pattern.search(s_clean):
                            found_skills.add(skill_name)
                            matched = True
                            break
                    if matched:
                        break
                if not matched and len(s_clean) <= 20:
                    found_skills.add(s_clean)

    if not text or not isinstance(text, str):
        return sorted(list(found_skills))

    text_lower = text.lower()
    for skill_name, patterns in COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text_lower):
                found_skills.add(skill_name)
                break

    return sorted(list(found_skills))
