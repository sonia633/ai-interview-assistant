"""Resume parsing service: extract text from PDF and structured fields."""
from __future__ import annotations

import re

import pdfplumber

from app.core.logging import get_logger
from app.schemas.resume import ParsedResume
from app.services.nlp_service import NLPService
from app.services.skills_data import HUMAN_LANGUAGES

logger = get_logger(__name__)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}"
)

EDU_KEYWORDS = ["education", "academic", "qualification", "degree", "university", "diploma"]
EXP_KEYWORDS = ["experience", "employment", "work history", "professional experience"]


class ResumeParser:
    def __init__(self) -> None:
        self.nlp = NLPService()

    # ----- PDF text -----
    def extract_text(self, path: str) -> str:
        text_parts: list[str] = []
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
        except Exception as exc:  # pragma: no cover - depends on file
            logger.warning("pdfplumber failed (%s), trying PyPDF2", exc)
            text_parts = [self._extract_with_pypdf2(path)]
        return "\n".join(text_parts).strip()

    @staticmethod
    def _extract_with_pypdf2(path: str) -> str:
        from PyPDF2 import PdfReader

        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    # ----- Structured fields -----
    def parse(self, path: str) -> ParsedResume:
        text = self.extract_text(path)
        lower = text.lower()

        email = self._first(EMAIL_RE, text)
        phone = self._extract_phone(text)
        name = self._guess_name(text, email)
        education = self._extract_section(text, EDU_KEYWORDS)
        experience = self._extract_section(text, EXP_KEYWORDS)
        languages = self._extract_languages(lower)

        technical, soft = self.nlp.extract_skills(text)

        return ParsedResume(
            candidate_name=name,
            email=email,
            phone=phone,
            education=education,
            experience=experience,
            languages=languages,
            raw_text=text,
            technical_skills=technical,
            soft_skills=soft,
        )

    # ----- helpers -----
    @staticmethod
    def _first(pattern: re.Pattern[str], text: str) -> str | None:
        m = pattern.search(text)
        return m.group(0).strip() if m else None

    def _extract_phone(self, text: str) -> str | None:
        for m in PHONE_RE.finditer(text):
            candidate = m.group(0).strip()
            digits = re.sub(r"\D", "", candidate)
            if 7 <= len(digits) <= 15:
                return candidate
        return None

    def _guess_name(self, text: str, email: str | None) -> str | None:
        # Try spaCy NER first, fall back to the first non-empty line.
        name = self.nlp.extract_person_name(text)
        if name:
            return name
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if email and email.lower() in line.lower():
                continue
            words = line.split()
            if 1 < len(words) <= 4 and all(w[0].isupper() for w in words if w[:1].isalpha()):
                return line
            break
        return None

    @staticmethod
    def _extract_section(text: str, keywords: list[str]) -> str | None:
        lines = text.splitlines()
        collected: list[str] = []
        capturing = False
        for line in lines:
            low = line.strip().lower()
            if any(low.startswith(k) for k in keywords):
                capturing = True
                continue
            if capturing:
                if low == "" and collected:
                    break
                if len(collected) >= 12:
                    break
                if line.strip():
                    collected.append(line.strip())
        return "\n".join(collected) if collected else None

    @staticmethod
    def _extract_languages(lower_text: str) -> str | None:
        found = [lang.title() for lang in HUMAN_LANGUAGES if re.search(rf"\b{lang}\b", lower_text)]
        return ", ".join(dict.fromkeys(found)) if found else None
