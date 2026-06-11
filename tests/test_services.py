"""Unit tests for AI/NLP services (no DB required)."""
from app.services.answer_evaluator import AnswerEvaluator
from app.services.nlp_service import NLPService
from app.services.question_generator import QuestionGenerator
from app.services.role_predictor import RolePredictor


def test_skill_extraction_counts_terms():
    nlp = NLPService()
    text = "I use Python and python with Docker, Kubernetes and teamwork and communication."
    technical, soft = nlp.extract_skills(text)
    assert technical.get("python", 0) >= 2
    assert "docker" in technical
    assert "teamwork" in soft
    assert "communication" in soft


def test_role_predictor_data_scientist():
    predictor = RolePredictor()
    text = "machine learning deep learning pytorch tensorflow nlp model training feature engineering"
    role, confidence = predictor.predict(text)
    assert role == "Data Scientist"
    assert 0.0 <= confidence <= 1.0


def test_role_predictor_devops():
    predictor = RolePredictor()
    role, _ = predictor.predict("docker kubernetes terraform aws ci cd jenkins infrastructure")
    assert role == "DevOps Engineer"


def test_question_generator_count_and_categories():
    gen = QuestionGenerator()
    qs = gen.generate("Software Engineer", ["python", "sql"], has_experience=True, num_questions=6)
    assert len(qs) == 6
    categories = {q["category"] for q in qs}
    assert categories <= {"technical", "behavioral", "problem_solving"}


def test_answer_evaluator_scores_range():
    ev = AnswerEvaluator()
    good = ev.evaluate(
        "How do you approach testing in Python?",
        "First, I write unit tests with pytest because they catch regressions early. "
        "For example, I achieved 90% coverage on my last project. Then I add integration "
        "tests, and finally I run them in CI for every pull request.",
    )
    empty = ev.evaluate("Any question?", "")
    assert 0 <= good["score"] <= 100
    assert good["score"] > empty["score"]
    assert empty["score"] == 0.0
    assert good["strengths"]
