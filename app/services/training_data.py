"""Seed training data for the job-role classifier.

In a real deployment this is replaced by a Kaggle resume dataset
(e.g. "Resume Dataset" / "updated-resume-dataset"). The shape is the
same: a list of (resume_text, role_label) pairs. The included samples
let the model train and run out-of-the-box inside the container.
"""

ROLES = [
    "Software Engineer",
    "Web Developer",
    "Data Analyst",
    "Data Scientist",
    "DevOps Engineer",
    "Cybersecurity Analyst",
]

# Several short synthetic samples per role. TF-IDF + LogisticRegression
# learns the discriminative vocabulary from these.
SEED_SAMPLES: list[tuple[str, str]] = [
    # Software Engineer
    ("software engineer building backend services in java and python with rest apis microservices oop design patterns unit testing git agile", "Software Engineer"),
    ("experienced software developer c++ algorithms data structures system design object oriented programming tdd code review scalable services", "Software Engineer"),
    ("backend engineer spring boot java api development sql database design clean architecture microservices kafka", "Software Engineer"),
    ("full stack software engineer python fastapi rest grpc design patterns testing continuous integration", "Software Engineer"),

    # Web Developer
    ("front end web developer html css javascript react bootstrap responsive design ui ux jquery tailwind", "Web Developer"),
    ("web developer building websites with react vue node express javascript typescript frontend backend", "Web Developer"),
    ("full stack web developer next.js node.js mongodb html css responsive single page applications", "Web Developer"),
    ("frontend engineer angular typescript css sass bootstrap web accessibility cross browser", "Web Developer"),

    # Data Analyst
    ("data analyst sql excel power bi tableau dashboards reporting data visualization business intelligence statistics", "Data Analyst"),
    ("business data analyst pandas sql excel reporting kpis dashboards data cleaning visualization tableau", "Data Analyst"),
    ("analytics specialist sql power bi data analysis reporting metrics excel pivot tables stakeholder", "Data Analyst"),
    ("data analyst python pandas numpy visualization matplotlib seaborn sql descriptive statistics reporting", "Data Analyst"),

    # Data Scientist
    ("data scientist machine learning python scikit-learn tensorflow deep learning nlp model training feature engineering statistics", "Data Scientist"),
    ("machine learning engineer pytorch deep learning computer vision nlp transformers model deployment data science", "Data Scientist"),
    ("data scientist predictive modeling regression classification clustering pandas numpy scikit-learn experimentation", "Data Scientist"),
    ("ml researcher deep learning neural networks nlp transformers python tensorflow keras feature engineering", "Data Scientist"),

    # DevOps Engineer
    ("devops engineer docker kubernetes terraform aws ci cd jenkins github actions infrastructure as code linux monitoring", "DevOps Engineer"),
    ("site reliability engineer kubernetes helm prometheus grafana aws terraform ansible automation pipelines linux", "DevOps Engineer"),
    ("devops cloud engineer azure docker kubernetes gitlab ci cd terraform infrastructure automation nginx", "DevOps Engineer"),
    ("platform engineer aws ecs kubernetes docker ci cd pipelines monitoring logging terraform ansible", "DevOps Engineer"),

    # Cybersecurity Analyst
    ("cybersecurity analyst penetration testing vulnerability assessment nmap wireshark metasploit owasp siem incident response firewall", "Cybersecurity Analyst"),
    ("security analyst soc siem splunk threat detection incident response vulnerability management network security firewall", "Cybersecurity Analyst"),
    ("information security engineer penetration testing burp suite owasp cryptography ids ips network security", "Cybersecurity Analyst"),
    ("cyber security specialist malware analysis incident response siem threat hunting vulnerability assessment", "Cybersecurity Analyst"),
]
