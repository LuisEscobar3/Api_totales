# Dockerfile for FastAPI + Playwright (sync_api) project
# Playwright base image already includes browsers & system deps
FROM mcr.microsoft.com/playwright/python:latest

WORKDIR /app

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app

# Expose the app port (project uses 4000 in run.py)
EXPOSE 4000

# (Optional) Ensure browsers are installed/up-to-date (usually preinstalled in this base image)
RUN playwright install --with-deps

# Start the API
# If you prefer Gunicorn with multiple workers:
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "-b", "0.0.0.0:4000", "--workers", "2"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4000", "--proxy-headers", "--forwarded-allow-ips", "*"]
