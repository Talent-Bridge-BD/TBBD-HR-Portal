# -----------------------------
# Stage 1: Build React frontend
# -----------------------------
FROM node:20-bookworm-slim AS frontend-build

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# -----------------------------
# Stage 2: FastAPI runtime
# -----------------------------
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Microsoft ODBC Driver 18 for SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl gnupg && curl -sSL -O https://packages.microsoft.com/config/debian/13/packages-microsoft-prod.deb && dpkg -i packages-microsoft-prod.deb && rm packages-microsoft-prod.deb && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY models ./models
COPY services ./services
COPY api ./api
COPY repositories ./repositories
COPY start.sh ./

COPY --from=frontend-build /frontend/dist ./dist

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
