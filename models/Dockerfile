FROM python:3.11-slim

WORKDIR /app

# Copy requirements.txt from one level above
COPY ../requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY models/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
