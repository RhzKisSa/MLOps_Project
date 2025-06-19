FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy entire source code into container
COPY . .

# Run the FastAPI service from models package
WORKDIR /app/models
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"]
