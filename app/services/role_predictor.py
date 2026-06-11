"""Job-role prediction using a TF-IDF + Logistic Regression pipeline.

The model is trained from `training_data.SEED_SAMPLES` (swap in a Kaggle
dataset for production) and cached to disk as a joblib artefact. Training
is lazy: the first prediction trains and persists the model; subsequent
calls load it from disk.
"""
from __future__ import annotations

import os

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from app.core.logging import get_logger
from app.services.training_data import ROLES, SEED_SAMPLES

logger = get_logger(__name__)

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_models", "role_clf.joblib")


class RolePredictor:
    _pipeline: Pipeline | None = None

    def __init__(self) -> None:
        if RolePredictor._pipeline is None:
            RolePredictor._pipeline = self._load_or_train()

    def _load_or_train(self) -> Pipeline:
        if os.path.exists(_MODEL_PATH):
            try:
                logger.info("Loading role model from %s", _MODEL_PATH)
                return joblib.load(_MODEL_PATH)
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to load model (%s); retraining.", exc)
        return self.train()

    def train(self) -> Pipeline:
        logger.info("Training role-prediction model on %d samples", len(SEED_SAMPLES))
        texts = [t for t, _ in SEED_SAMPLES]
        labels = [r for _, r in SEED_SAMPLES]
        pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
                ("clf", LogisticRegression(max_iter=1000, C=4.0)),
            ]
        )
        pipeline.fit(texts, labels)
        os.makedirs(os.path.dirname(_MODEL_PATH), exist_ok=True)
        joblib.dump(pipeline, _MODEL_PATH)
        RolePredictor._pipeline = pipeline
        return pipeline

    def predict(self, text: str) -> tuple[str, float]:
        """Return (role, confidence 0..1)."""
        if not text or not text.strip():
            return ROLES[0], 0.0
        pipeline = RolePredictor._pipeline
        assert pipeline is not None
        probs = pipeline.predict_proba([text])[0]
        classes = list(pipeline.named_steps["clf"].classes_)
        best_idx = int(probs.argmax())
        return classes[best_idx], float(probs[best_idx])

    def predict_ranked(self, text: str) -> list[tuple[str, float]]:
        pipeline = RolePredictor._pipeline
        assert pipeline is not None
        probs = pipeline.predict_proba([text])[0]
        classes = list(pipeline.named_steps["clf"].classes_)
        ranked = sorted(zip(classes, map(float, probs)), key=lambda x: x[1], reverse=True)
        return ranked
