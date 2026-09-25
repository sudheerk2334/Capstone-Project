# Support Assistant

A document-grounded support assistant implemented with FastAPI.

## Architecture

```text
User question
     |
     v
Router
  /   \
 /     \
Policy  General
 |        |
Retrieve Direct
 |        |
 +---+----+
     |
  JSON response
```

### Key features

- 8 local support documents
- keyword/semantic-style retrieval using token overlap
- deterministic `MOCK_LLM` mode by default
- policy questions are grounded in retrieved documents
- general questions are answered directly
- confidence score and source documents are returned
- low-confidence requests can be escalated
- conversation history is retained per session
- no network call is made in default mock mode

## Run locally

From the repository root:

```bash
python support_assistant/app.py
```

Or:

```bash
uvicorn support_assistant.app:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`

Example request:

```json
{
  "question": "I forgot my password",
  "session_id": "demo"
}
```

## Docker

```bash
docker build -t zepto-support-assistant support_assistant
docker run --rm -p 8000:8000 zepto-support-assistant
```
