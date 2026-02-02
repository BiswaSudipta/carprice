# -------- Base Image --------
FROM python:3.10-slim

# -------- Set Working Directory --------
WORKDIR /app

# -------- Install System Dependencies --------
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# -------- Copy Requirements --------
COPY requirements.txt .

# -------- Install Python Dependencies --------
RUN pip install --no-cache-dir -r requirements.txt

# -------- Copy App Files --------
COPY . .

# -------- Expose Port --------
EXPOSE 8000

# -------- Start FastAPI --------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
