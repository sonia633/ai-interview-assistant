"""Evaluate a candidate's free-text answer and produce a 0-100 score
plus feedback, strengths and weaknesses.

The heuristic scorer combines several interpretable signals (length,
structure, keyword relevance, concrete examples, hedging) so the score
is explainable. It is deliberately model-agnostic and runs offline; a
transformer-based scorer can be swapped in behind the same interface.
"""
from __future__ import annotations

import re

from app.services.skills_data import SOFT_SKILLS, TECHNICAL_SKILLS

_ALL_KEYWORDS = set(TECHNICAL_SKILLS) | set(SOFT_SKILLS)

_STRUCTURE_MARKERS = [
    "first", "second", "then", "finally", "because", "therefore",
    "for example", "such as", "as a result", "however",
]
_HEDGING = ["maybe", "i guess", "not sure", "i think probably", "kind of", "sort of"]
_CONCRETE = re.compile(r"\b\d+%?\b|\bfor example\b|\bsuch as\b|\be\.g\.\b")


class AnswerEvaluator:
    def evaluate(self, question: str, answer: str) -> dict:
        answer = (answer or "").strip()
        words = answer.split()
        wc = len(words)

        strengths: list[str] = []
        weaknesses: list[str] = []

        # --- Length signal (0..30) ---
        if wc == 0:
            return {
                "score": 0.0,
                "feedback": "No answer was provided.",
                "strengths": [],
                "weaknesses": ["The answer is empty."],
            }
        if wc < 15:
            length_score = wc / 15 * 18
            weaknesses.append("The answer is quite short — add more detail and context.")
        elif wc <= 220:
            length_score = 30
            strengths.append("Good level of detail and appropriate length.")
        else:
            length_score = 24
            weaknesses.append("The answer is long — be more concise and focused.")

        # --- Structure signal (0..20) ---
        lower = answer.lower()
        markers = sum(1 for m in _STRUCTURE_MARKERS if m in lower)
        structure_score = min(markers, 5) / 5 * 20
        if markers >= 3:
            strengths.append("Well-structured with clear logical flow.")
        elif markers == 0:
            weaknesses.append("Add connecting words to show your reasoning step by step.")

        # --- Relevance signal (0..30) ---
        q_terms = {w.strip(".,") for w in question.lower().split() if len(w) > 4}
        overlap = sum(1 for t in q_terms if t in lower)
        kw_hits = sum(1 for k in _ALL_KEYWORDS if re.search(rf"(?<!\w){re.escape(k)}(?!\w)", lower))
        relevance_raw = min(overlap, 6) / 6 * 18 + min(kw_hits, 4) / 4 * 12
        relevance_score = relevance_raw
        if kw_hits >= 2:
            strengths.append("Mentions concrete, relevant technical terms.")
        if overlap == 0:
            weaknesses.append("The answer doesn't clearly address the question asked.")

        # --- Concreteness signal (0..15) ---
        concrete_hits = len(_CONCRETE.findall(lower))
        concrete_score = min(concrete_hits, 3) / 3 * 15
        if concrete_hits:
            strengths.append("Includes specific examples or measurable details.")
        else:
            weaknesses.append("Back up your points with a concrete example or metric.")

        # --- Confidence penalty (0..-5) ---
        hedges = sum(1 for h in _HEDGING if h in lower)
        confidence_penalty = min(hedges, 5)
        if hedges >= 2:
            weaknesses.append("Avoid hedging language — answer with more confidence.")

        total = (
            length_score
            + structure_score
            + relevance_score
            + concrete_score
            + 5  # base
            - confidence_penalty
        )
        score = round(max(0.0, min(100.0, total)), 1)

        feedback = self._build_feedback(score, strengths, weaknesses)
        return {
            "score": score,
            "feedback": feedback,
            "strengths": strengths or ["You provided a relevant response."],
            "weaknesses": weaknesses or ["No major weaknesses detected — keep refining."],
        }

    @staticmethod
    def _build_feedback(score: float, strengths: list[str], weaknesses: list[str]) -> str:
        if score >= 80:
            verdict = "Excellent answer."
        elif score >= 60:
            verdict = "Good answer with room to improve."
        elif score >= 40:
            verdict = "Average answer — several areas to strengthen."
        else:
            verdict = "Weak answer — significant improvement needed."
        return (
            f"{verdict} Score: {score}/100. "
            f"Strengths: {len(strengths)} identified. "
            f"Focus next on: {weaknesses[0] if weaknesses else 'consistency'}"
        )
