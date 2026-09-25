# Zepto Platform

An end-to-end Python project containing three independent components:

1. **Data Pipeline** – SQLite-based product catalog ETL pipeline.
2. **Analytics** – Titanic analytics and a reusable scikit-learn pipeline.
3. **Support Assistant** – document-grounded support assistant with deterministic mock LLM behavior, confidence tracking, escalation, and optional Docker deployment.

## Project Structure

```text
zepto_platform/
├── README.md
├── requirements.txt
├── .gitignore
├── data_pipeline/
│   ├── README.md
│   ├── pipeline.py
│   └── zepto_catalog.db
├── analytics/
│   ├── README.md
│   ├── titanic.csv
│   ├── run_analytics.py
│   └── full_pipeline.joblib
└── support_assistant/
    ├── README.md
    ├── Dockerfile
    ├── app.py
    └── docs/
        ├── doc_01.txt
        ├── doc_02.txt
        ├── doc_03.txt
        ├── doc_04.txt
        ├── doc_05.txt
        ├── doc_06.txt
        ├── doc_07.txt
        └── doc_08.txt
```

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Run Data Pipeline

```bash
python data_pipeline/pipeline.py
```

## Run Analytics

```bash
python analytics/run_analytics.py
```

## Run Support Assistant

```bash
python support_assistant/app.py
```

The support assistant defaults to `MOCK_LLM=1`, so it does not make network calls.

## Docker

```bash
docker build -t zepto-support-assistant ./support_assistant
docker run --rm -p 8000:8000 zepto-support-assistant
```

Then open `http://localhost:8000/docs`.
