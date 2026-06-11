"""Generate personalised interview questions.

Questions are built from templates parameterised by the candidate's
top skills, predicted role and experience. Categories: technical,
behavioral, problem_solving.
"""
from __future__ import annotations

ROLE_TECH_TOPICS: dict[str, list[str]] = {
    "Software Engineer": ["system design", "object-oriented design", "API design", "testing strategy", "concurrency"],
    "Web Developer": ["responsive design", "state management", "REST APIs", "browser performance", "accessibility"],
    "Data Analyst": ["SQL query optimisation", "data cleaning", "dashboard design", "A/B testing", "KPI definition"],
    "Data Scientist": ["feature engineering", "model evaluation", "overfitting", "the bias-variance tradeoff", "NLP pipelines"],
    "DevOps Engineer": ["CI/CD pipelines", "container orchestration", "infrastructure as code", "observability", "zero-downtime deploys"],
    "Cybersecurity Analyst": ["threat modelling", "incident response", "the OWASP Top 10", "network segmentation", "vulnerability triage"],
}

BEHAVIORAL_TEMPLATES = [
    "Tell me about a time you had a conflict with a teammate. How did you resolve it?",
    "Describe a project you are most proud of and your specific contribution.",
    "Give an example of when you had to learn a new technology quickly.",
    "Tell me about a deadline you missed. What did you learn?",
    "Describe a situation where you received difficult feedback and how you responded.",
    "How do you prioritise when everything feels urgent?",
]

PROBLEM_SOLVING_TEMPLATES = [
    "How would you debug a service that intermittently returns 500 errors in production?",
    "Walk me through how you would design a URL shortener.",
    "You notice a data pipeline is suddenly 10x slower. How do you investigate?",
    "How would you reduce the load time of a slow web page?",
    "Estimate how much storage you would need to log every request to a busy API for a year.",
]


class QuestionGenerator:
    def generate(
        self,
        role: str | None,
        top_skills: list[str],
        has_experience: bool,
        num_questions: int = 6,
    ) -> list[dict[str, str]]:
        questions: list[dict[str, str]] = []

        # ---- Technical (skill + role driven) ----
        tech_questions: list[str] = []
        for skill in top_skills[:4]:
            tech_questions.append(
                f"Can you explain how you have used {skill} in a real project, "
                f"and a limitation you ran into?"
            )
        for topic in ROLE_TECH_TOPICS.get(role or "", [])[:3]:
            tech_questions.append(f"As a {role}, how do you approach {topic}?")
        if not tech_questions:
            tech_questions.append("Which technology in your stack do you know most deeply, and why?")

        # ---- Behavioral ----
        behavioral = list(BEHAVIORAL_TEMPLATES)
        if has_experience:
            behavioral.insert(0, "Describe your most recent role and your biggest impact there.")

        # ---- Problem solving ----
        problem = list(PROBLEM_SOLVING_TEMPLATES)

        # ---- Interleave to fill num_questions ----
        buckets = [
            ("technical", tech_questions),
            ("behavioral", behavioral),
            ("problem_solving", problem),
        ]
        idx = 0
        cursors = {name: 0 for name, _ in buckets}
        while len(questions) < num_questions:
            name, pool = buckets[idx % len(buckets)]
            c = cursors[name]
            if c < len(pool):
                questions.append({"category": name, "text": pool[c]})
                cursors[name] = c + 1
            idx += 1
            # Safety break if every pool exhausted
            if all(cursors[n] >= len(p) for n, p in buckets):
                break
        return questions[:num_questions]
