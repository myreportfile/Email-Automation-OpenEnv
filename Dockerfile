FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt || true
RUN pip install pydantic fastapi uvicorn openenv-core

CMD ["python", "inference.py"]