# 🤖 AI Interview Assistant

<!-- doc-pdf -->
## 📄 Explication du code

📥 **[Télécharger le PDF d'explication du code](EXPLICATION-CODE.pdf)** — architecture, fichiers principaux, API et démarrage, expliqués pas à pas.

A production-ready web platform that helps candidates prepare for job interviews using AI.
Upload your resume, let the system **parse it**, **extract your skills**, **predict your
ideal job role**, generate **personalised interview questions**, and receive **scored
feedback** on every answer — all wrapped in a clean Bootstrap UI with a Chart.js dashboard.

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Authentication** | Register, login, logout, bcrypt hashing, JWT + secure cookie sessions, user profiles |
| 2 | **Resume upload** | PDF upload with size/type validation and secure storage |
| 3 | **Resume parsing** | Extracts name, email, phone, skills, education, experience, languages |
| 4 | **NLP skill extraction** | Technical vs. soft skills, frequency counts, skill summary (spaCy + regex) |
| 5 | **Job-role prediction** | TF-IDF + Logistic Regression model over 6 roles (Kaggle-ready) |
| 6 | **AI question generator** | Personalised technical / behavioral / problem-solving questions |
| 7 | **Answer evaluation** | Explainable 0–100 score with strengths & weaknesses |
| 8 | **Dashboard** | Total interviews, average score, skill distribution, progress (Chart.js) |
| 9 | **Interview history** | All past sessions, scores and comparison |
| 10 | **Admin panel** | User management, dataset/model management, system statistics, logs |

## 🧱 Tech Stack

**Backend:** Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL
**AI/NLP:** scikit-learn · spaCy · Transformers · Pandas · NumPy · pdfplumber / PyPDF2
**Frontend:** Jinja2 · Bootstrap 5 · Chart.js
**Ops:** Docker · Docker Compose · GitHub Actions · Pytest

## 🏛️ Architecture (Clean Architecture)

```
app/
├── api/          # FastAPI routers (HTTP layer) + dependencies
├── core/         # config, database, security, logging (cross-cutting)
├── models/       # SQLAlchemy ORM entities
├── schemas/      # Pydantic DTOs (validation / serialisation)
├── repositories/ # data-access layer (DB queries)
├── services/     # business logic + AI/NLP/ML
├── templates/    # Jinja2 HTML (Bootstrap)
└── static/       # CSS / JS / Chart.js glue
```

The dependency direction flows **inward**: routers depend on services, services depend on
repositories and models. Cross-cutting concerns live in `core/`. See
[docs/architecture.md](docs/architecture.md).

## 🚀 Quick start (Docker)

```bash
# 1. Clone & configure
cp .env.example .env          # adjust secrets if you like

# 2. Build & run everything (FastAPI + PostgreSQL)
docker compose up -d

# 3. Open the app
#    UI      -> http://localhost:8000
#    API docs-> http://localhost:8000/docs
```

The container automatically waits for PostgreSQL, runs **Alembic migrations**, seeds a
default **admin** account and starts Uvicorn.

**Default admin** (change in `.env`): `admin@interview.ai` / `Admin12345!`

## 🧑‍💻 Local development (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm             # optional (NLP name detection)

# Point DATABASE_URL at a local Postgres, or use SQLite for a quick spin:
export DATABASE_URL="sqlite+pysqlite:///./dev.db"
export SECRET_KEY=dev SECRET JWT_SECRET_KEY=dev-jwt

uvicorn app.main:app --reload
```

> Tables are auto-created on startup for frictionless local dev; in Docker, **Alembic** is
> the source of truth.

## ✅ Testing

```bash
pytest -q
```

Tests run against an isolated SQLite database and cover authentication, the AI/NLP
services and the full interview API flow.

## 📚 Documentation

- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)
- [Database schema](docs/database.md)
- Interactive API docs (Swagger): `/docs` · ReDoc: `/redoc`

## 🔐 Security

- Passwords hashed with **bcrypt**
- **JWT** auth (header) + httponly, samesite cookies for the browser
- Parameterised queries via SQLAlchemy ORM (no string-built SQL)
- Pydantic input validation on every endpoint
- Jinja2 autoescaping + client-side escaping (XSS)
- Secure file uploads (extension, content-type, size, sanitised filenames, random names)
- All secrets via environment variables

## 📝 License

MIT — free to use for your professional portfolio.
