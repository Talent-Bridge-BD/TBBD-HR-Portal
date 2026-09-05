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

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY start.sh ./

# React production build
COPY --from=frontend-build /frontend/dist ./dist

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
