"""Interview flow API tests (create -> questions -> answer -> score)."""


def test_full_interview_flow(auth_client):
    # Create an interview (no resume, generic role)
    r = auth_client.post(
        "/api/interviews",
        json={"resume_id": None, "role": "Software Engineer", "num_questions": 4},
    )
    assert r.status_code == 201, r.text
    interview_id = r.json()["id"]

    # Fetch generated questions
    r = auth_client.get(f"/api/interviews/{interview_id}/questions")
    assert r.status_code == 200
    questions = r.json()
    assert len(questions) == 4

    # Submit an answer and get evaluation
    qid = questions[0]["id"]
    r = auth_client.post(
        "/api/interviews/answers",
        json={
            "question_id": qid,
            "text": "First I design the API, then I write unit tests because testing "
                    "matters, and finally I deploy. For example I used FastAPI in production.",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert 0 <= body["score"] <= 100
    assert "feedback" in body

    # Dashboard reflects the interview
    r = auth_client.get("/api/dashboard/overview")
    assert r.status_code == 200
    assert r.json()["total_interviews"] == 1


def test_interview_requires_auth(client):
    assert client.post("/api/interviews", json={"num_questions": 4}).status_code == 401
