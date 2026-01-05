# 1. Base image
FROM python:3.12-slim

# 2. Set work dir
WORKDIR /app

# 3. System deps (optional: curl for debugging, build deps if you need them)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy dependency lists first (better layer caching)
COPY requirements.txt .

# 5. Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the app code
COPY . .

# 7. Expose Shiny port (default 8000)
EXPOSE 8000

# 8. Run the Shiny app
# --host 0.0.0.0 so it’s reachable from outside the container
CMD ["shiny", "run", "--host", "0.0.0.0", "--port", "8000", "app.py"]
