FROM python:3.11-slim

WORKDIR /app

COPY ../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app/support_assistant

EXPOSE 8000

CMD ["uvicorn", "support_assistant.app:app", "--host", "0.0.0.0", "--port", "8000"]
