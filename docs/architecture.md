# Architecture

The project follows **Clean Architecture** principles: business logic is isolated from
frameworks and I/O, and dependencies point inward.

## Layers

```
┌─────────────────────────────────────────────────────────────┐
│                       Presentation                          │
│   app/api/routes/*  (FastAPI routers, Jinja2 pages)         │
│   app/templates, app/static  (Bootstrap 5 + Chart.js UI)   │
└───────────────┬─────────────────────────────────────────────┘
                │ depends on
┌───────────────▼─────────────────────────────────────────────┐
│                        Services                             │
│  auth · resume_parser · nlp · role_predictor ·              │
│  question_generator · answer_evaluator · interview ·        │
│  dashboard · storage        (pure business / AI logic)      │
└───────────────┬─────────────────────────────────────────────┘
                │ depends on
┌───────────────▼─────────────────────────────────────────────┐
│                      Repositories                           │
│   user_repo · resume_repo · interview_repo  (DB access)     │
└───────────────┬─────────────────────────────────────────────┘
                │ depends on
┌───────────────▼─────────────────────────────────────────────┐
│                    Models / Schemas                         │
│   SQLAlchemy ORM entities  +  Pydantic DTOs                 │
└───────────────┬─────────────────────────────────────────────┘
                │ uses
┌───────────────▼─────────────────────────────────────────────┐
│                         Core                                │
│   config · database · security · logging  (cross-cutting)   │
└─────────────────────────────────────────────────────────────┘
```

## Request lifecycle (example: submit an answer)

1. `POST /api/interviews/answers` hits `api/routes/interviews.py`.
2. The router validates the body with `schemas/interview.py:AnswerSubmit`.
3. `deps.get_current_user` decodes the JWT (cookie/header) and loads the `User`.
4. `services/interview_service.py` calls `services/answer_evaluator.py` to score the text.
5. The answer + score are persisted via the ORM, the interview's aggregate `Score` is
   recomputed, and a JSON `AnswerEvaluation` is returned.

## AI / ML components

| Component | Technique | File |
|-----------|-----------|------|
| Skill extraction | Vocabulary + word-boundary regex, optional spaCy NER for names | `services/nlp_service.py` |
| Role prediction | TF-IDF (1–2 grams) → Logistic Regression, cached with joblib | `services/role_predictor.py` |
| Question generation | Role/skill-parameterised templates, category interleaving | `services/question_generator.py` |
| Answer evaluation | Interpretable multi-signal scorer (length, structure, relevance, concreteness) | `services/answer_evaluator.py` |

The role model trains from `services/training_data.py`. To use a real **Kaggle resume
dataset**, replace `SEED_SAMPLES` with `(resume_text, role_label)` pairs loaded with
Pandas and call the admin **Retrain** endpoint.

## Why this structure scales

- **Swappable AI** — every model sits behind a service interface, so a Transformer-based
  scorer or an LLM can replace the heuristic without touching routers or the DB.
- **Testable** — services are plain Python with no FastAPI/DB coupling (see `tests/`).
- **Migration-safe** — Alembic owns the schema; models stay declarative.
