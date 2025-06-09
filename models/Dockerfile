FROM python:3.11-slim

WORKDIR /app

# Copy requirements.txt from one level above
COPY ../requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "8081"]
