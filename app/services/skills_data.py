"""Skill vocabularies used by the NLP extraction service.

These lists are intentionally broad and editable. They are matched
case-insensitively against resume text using word-boundary regexes.
"""

TECHNICAL_SKILLS: list[str] = [
    # Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
    "bash", "shell", "perl", "dart",
    # Web / frameworks
    "html", "css", "react", "angular", "vue", "svelte", "node", "node.js",
    "express", "django", "flask", "fastapi", "spring", "spring boot",
    "laravel", "rails", "next.js", "nuxt", "bootstrap", "tailwind", "jquery",
    # Data / ML
    "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch",
    "keras", "spacy", "nltk", "transformers", "matplotlib", "seaborn",
    "power bi", "tableau", "excel", "spark", "hadoop", "airflow", "dbt",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data science", "statistics",
    # Databases
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
    "cassandra", "elasticsearch", "oracle", "dynamodb", "snowflake",
    # DevOps / cloud
    "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "terraform",
    "ansible", "jenkins", "github actions", "gitlab ci", "ci/cd", "linux",
    "nginx", "apache", "prometheus", "grafana", "helm",
    # Security
    "penetration testing", "nmap", "wireshark", "metasploit", "burp suite",
    "owasp", "siem", "splunk", "cryptography", "firewall", "ids", "ips",
    "vulnerability assessment", "incident response",
    # Tools / general
    "git", "github", "gitlab", "jira", "rest", "graphql", "grpc",
    "microservices", "agile", "scrum", "tdd", "oop",
]

SOFT_SKILLS: list[str] = [
    "communication", "teamwork", "leadership", "problem solving",
    "problem-solving", "critical thinking", "creativity", "adaptability",
    "time management", "collaboration", "organization", "mentoring",
    "presentation", "negotiation", "decision making", "attention to detail",
    "analytical", "self-motivated", "flexibility", "empathy", "ownership",
]

# Common human languages (for the "languages" field of a resume).
HUMAN_LANGUAGES: list[str] = [
    "english", "french", "spanish", "german", "arabic", "chinese",
    "mandarin", "hindi", "portuguese", "russian", "japanese", "italian",
    "korean", "dutch", "turkish", "polish",
]
