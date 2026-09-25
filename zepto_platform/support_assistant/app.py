"""
Document-grounded support assistant.

Default mode:
    MOCK_LLM=1

No network call is made in mock mode.
"""

from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
MOCK_LLM = os.getenv("MOCK_LLM", "1").lower() not in {"0", "false", "no"}

app = FastAPI(title="Zepto Support Assistant", version="1.0.0")

SESSIONS: Dict[str, List[dict]] = {}


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = None


class Source(BaseModel):
    document: str
    title: str
    score: float


class AnswerResponse(BaseModel):
    answer: str
    question_type: str
    confidence: float
    sources: List[Source]
    session_id: str
    escalated: bool
    ticket_id: str | None = None


def tokenize(text: str) -> set[str]:
    stop_words = {
        "the", "a", "an", "is", "are", "to", "of", "for", "and",
        "i", "my", "me", "can", "how", "what", "do", "does", "on"
    }
    return {
        token for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in stop_words
    }


def load_documents() -> list[dict]:
    documents = []
    for path in sorted(DOCS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        lines = text.strip().splitlines()
        title = lines[0].replace("Title:", "").strip() if lines else path.stem
        documents.append(
            {
                "document": path.name,
                "title": title,
                "text": text,
                "tokens": tokenize(text),
            }
        )
    return documents


DOCUMENTS = load_documents()


def classify_question(question: str) -> str:
    q = question.lower()
    policy_terms = {
        "password", "login", "refund", "return", "cancel", "cancellation",
        "delivery", "payment", "charged", "support hours", "otp", "privacy",
        "data", "order", "dispatch", "locked"
    }
    return "policy_question" if any(term in q for term in policy_terms) else "general_question"


def retrieve(question: str, top_k: int = 3) -> list[dict]:
    q_tokens = tokenize(question)
    if not q_tokens:
        return []

    scored = []
    for doc in DOCUMENTS:
        overlap = len(q_tokens & doc["tokens"])
        # Normalize lightly so longer documents do not automatically win.
        score = overlap / max(len(q_tokens), 1)
        if score > 0:
            scored.append({**doc, "score": round(min(score, 1.0), 3)})

    return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]


def mock_grounded_answer(question: str, results: list[dict]) -> str:
    if not results:
        return (
            "I could not find a relevant policy in the support documents. "
            "Please contact customer support for further assistance."
        )

    best = results[0]
    text = best["text"].strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    useful = " ".join(sentences[1:4]).strip()

    if not useful:
        useful = text

    return f"According to {best['title']}: {useful}"


def direct_answer(question: str) -> str:
    q = question.lower()

    if "hello" in q or "hi" in q:
        return "Hello! How can I help you today?"
    if "thank" in q:
        return "You're welcome. I'm happy to help."
    if "who are you" in q:
        return "I'm the Zepto support assistant. I can help with documented support policies and common questions."

    return (
        "I can help with support policies such as password reset, login, refunds, "
        "cancellation, delivery, payments, support hours, and personal-data handling."
    )


def build_response(request: AskRequest) -> AnswerResponse:
    session_id = request.session_id or str(uuid.uuid4())
    SESSIONS.setdefault(session_id, []).append(
        {"role": "user", "content": request.question}
    )

    question_type = classify_question(request.question)

    if question_type == "policy_question":
        results = retrieve(request.question)
        confidence = results[0]["score"] if results else 0.0
        answer = mock_grounded_answer(request.question, results)

        sources = [
            Source(
                document=r["document"],
                title=r["title"],
                score=r["score"],
            )
            for r in results
        ]
    else:
        results = []
        confidence = 0.9
        answer = direct_answer(request.question)
        sources = []

    escalated = confidence < 0.30
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}" if escalated else None

    if escalated:
        answer += (
            f" I have escalated this request for human support"
            f" under ticket {ticket_id}."
        )

    SESSIONS[session_id].append({"role": "assistant", "content": answer})

    return AnswerResponse(
        answer=answer,
        question_type=question_type,
        confidence=round(confidence, 3),
        sources=sources,
        session_id=session_id,
        escalated=escalated,
        ticket_id=ticket_id,
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "documents": len(DOCUMENTS),
        "mock_llm": MOCK_LLM,
    }


@app.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest):
    return build_response(request)


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    return {
        "session_id": session_id,
        "messages": SESSIONS.get(session_id, []),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)