# API Reference

Base URL: `http://localhost:8000`
Interactive docs: `/docs` (Swagger UI) · `/redoc` (ReDoc)

Authentication uses a **JWT**. After `login`, the token is returned in the body **and**
set as an httponly cookie. API clients may instead send `Authorization: Bearer <token>`.

## Auth

| Method | Path | Auth | Body | Description |
|--------|------|------|------|-------------|
| POST | `/api/auth/register` | – | `{full_name, email, password}` | Create an account |
| POST | `/api/auth/login` | – | `{email, password}` | Get JWT + set cookie |
| POST | `/api/auth/logout` | – | – | Clear the cookie |
| GET | `/api/auth/me` | ✅ | – | Current user profile |

## Resumes

| Method | Path | Auth | Body | Description |
|--------|------|------|------|-------------|
| POST | `/api/resumes/upload` | ✅ | `multipart: file` | Upload PDF, parse, predict role |
| GET | `/api/resumes` | ✅ | – | List your resumes |
| GET | `/api/resumes/{id}` | ✅ | – | Resume detail |

## Interviews

| Method | Path | Auth | Body | Description |
|--------|------|------|------|-------------|
| POST | `/api/interviews` | ✅ | `{resume_id?, role?, num_questions}` | Start a session, generate questions |
| GET | `/api/interviews` | ✅ | – | List your interviews |
| GET | `/api/interviews/{id}/questions` | ✅ | – | Questions for a session |
| POST | `/api/interviews/answers` | ✅ | `{question_id, text}` | Submit & score an answer |

## Dashboard

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/dashboard/overview` | ✅ | Totals, average score, progress, skill distribution |

## Admin (requires `is_admin`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/admin/users` | List all users |
| PATCH | `/api/admin/users/{id}/toggle-active` | Enable/disable a user |
| GET | `/api/admin/stats` | System counts |
| GET | `/api/admin/dataset` | Role dataset info |
| POST | `/api/admin/model/retrain` | Retrain the role model |
| GET | `/api/admin/logs` | Recent audit logs |

## Example

```bash
# Register
curl -X POST localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"full_name":"Jane Doe","email":"jane@x.com","password":"password1"}'

# Login (capture cookie)
curl -c cookies.txt -X POST localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"jane@x.com","password":"password1"}'

# Start an interview
curl -b cookies.txt -X POST localhost:8000/api/interviews \
  -H 'Content-Type: application/json' \
  -d '{"role":"Data Scientist","num_questions":5}'
```

### Sample answer-evaluation response

```json
{
  "question_id": 12,
  "score": 78.5,
  "feedback": "Good answer with room to improve. Score: 78.5/100. ...",
  "strengths": ["Well-structured with clear logical flow.", "Mentions concrete, relevant technical terms."],
  "weaknesses": ["Back up your points with a concrete example or metric."]
}
```
