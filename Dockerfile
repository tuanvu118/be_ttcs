# Dockerfile
FROM python:3.11-slim

# Không tạo .pyc + log ra terminal ngay
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# (Tuỳ lib) cài gói hệ thống tối thiểu để tránh lỗi build bcrypt/argon2 trên linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài dependencies trước để tận dụng cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY . /app

# Expose port
EXPOSE 8000

# Chạy app
# Sửa "main:app" nếu entrypoint của bạn khác
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
