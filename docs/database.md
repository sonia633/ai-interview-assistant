# Database Schema

PostgreSQL, normalised (3NF). Managed by Alembic (`alembic/versions/0001_initial.py`).

## Entity-Relationship Diagram

```
 users 1───∞ resumes 1───∞ resume_skills ∞───1 skills
   │              │
   │              └────────∞ interviews 1───∞ questions 1───1 answers
   │                            │
   │                            └───1 scores
   └───────────∞ logs
```

## Tables

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| full_name | varchar(150) | |
| email | varchar(255) | unique, indexed |
| hashed_password | varchar(255) | bcrypt |
| is_active | bool | default true |
| is_admin | bool | default false |
| created_at | timestamptz | |

### `resumes`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK→users | on delete CASCADE |
| original_filename | varchar(255) | |
| stored_path | varchar(512) | server path |
| file_size | int | bytes |
| candidate_name / email / phone | varchar | parsed |
| education / experience / languages / raw_text | text | parsed |
| predicted_role | varchar(100) | ML output |
| role_confidence | float | 0–1 |
| created_at | timestamptz | |

### `skills`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| name | varchar(100) | unique, indexed |
| category | varchar(20) | `technical` \| `soft` |

### `resume_skills` (association)
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| resume_id | int FK→resumes | CASCADE |
| skill_id | int FK→skills | CASCADE |
| frequency | int | occurrences in resume |

### `interviews`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK→users | CASCADE |
| resume_id | int FK→resumes | nullable, SET NULL |
| role | varchar(100) | |
| status | varchar(20) | `in_progress` \| `completed` |
| created_at | timestamptz | |

### `questions`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| interview_id | int FK→interviews | CASCADE |
| category | varchar(30) | `technical` \| `behavioral` \| `problem_solving` |
| text | text | |

### `answers`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| question_id | int FK→questions | unique, CASCADE |
| text | text | candidate answer |
| score | float | 0–100 |
| feedback / strengths / weaknesses | text | evaluation output |

### `scores` (aggregate per interview)
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| interview_id | int FK→interviews | unique, CASCADE |
| average_score | float | mean of answered questions |
| total_questions | int | |
| answered_questions | int | |

### `logs` (audit)
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK→users | nullable, SET NULL |
| action | varchar(100) | e.g. `login`, `resume_upload` |
| detail | text | |
| created_at | timestamptz | indexed |
```
