"""NLP service: skill extraction + frequency, and person-name detection.

Uses spaCy when the `en_core_web_sm` model is available, but degrades
gracefully to pure-regex matching so the app runs even without it.
"""
from __future__ import annotations

import re
from collections import Counter

from app.core.logging import get_logger
from app.services.skills_data import SOFT_SKILLS, TECHNICAL_SKILLS

logger = get_logger(__name__)


def _load_spacy():
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except Exception as exc:  # pragma: no cover - depends on environment
        logger.info("spaCy model unavailable (%s); using regex fallback.", exc)
        return None


class NLPService:
    _nlp = None
    _loaded = False

    def __init__(self) -> None:
        if not NLPService._loaded:
            NLPService._nlp = _load_spacy()
            NLPService._loaded = True

    # ----- skills -----
    def extract_skills(self, text: str) -> tuple[dict[str, int], dict[str, int]]:
        lower = text.lower()
        technical = self._count_terms(lower, TECHNICAL_SKILLS)
        soft = self._count_terms(lower, SOFT_SKILLS)
        return technical, soft

    @staticmethod
    def _count_terms(lower_text: str, vocabulary: list[str]) -> dict[str, int]:
        counts: Counter[str] = Counter()
        for term in vocabulary:
            pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
            hits = len(re.findall(pattern, lower_text))
            if hits:
                counts[term] = hits
        return dict(counts.most_common())

    # ----- name -----
    def extract_person_name(self, text: str) -> str | None:
        if not self._nlp:
            return None
        # Only look at the top of the document where the name usually lives.
        doc = self._nlp(text[:400])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()
        return None

    # ----- summary -----
    def skill_summary(self, technical: dict[str, int], soft: dict[str, int]) -> str:
        top_tech = list(technical.keys())[:5]
        top_soft = list(soft.keys())[:3]
        parts = []
        if top_tech:
            parts.append("Top technical skills: " + ", ".join(top_tech))
        if top_soft:
            parts.append("Soft skills: " + ", ".join(top_soft))
        if not parts:
            return "No recognisable skills were detected in this resume."
        return ". ".join(parts) + "."
