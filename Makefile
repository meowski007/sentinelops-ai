.PHONY: help install seed eval test lint build backend frontend docker-up

help:
	@echo "SentinelOps AI - Development Commands:"
	@echo "  make install        Install backend and frontend dependencies"
	@echo "  make seed           Seed synthetic IT operations database"
	@echo "  make eval           Run RAG retrieval benchmark (MRR, Recall@K)"
	@echo "  make test           Run all unit and integration tests"
	@echo "  make lint           Run Ruff linting"
	@echo "  make build          Build frontend production bundle"
	@echo "  make backend        Start FastAPI backend server"
	@echo "  make frontend       Start Vite React dev server"
	@echo "  make docker-up      Start containerized stack via Docker Compose"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && python -m app.scripts.seed_data

eval:
	cd backend && python -m app.scripts.run_eval

test:
	cd backend && pytest
	cd frontend && npm test

lint:
	cd backend && ruff check .

build:
	cd frontend && npm run build

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build
