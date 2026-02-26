# Global Tax-Code Translator Agent - Makefile
# Convenient commands for development and deployment

.PHONY: help install run dev docker-build docker-run clean test

# Default target
help:
	@echo "Global Tax-Code Translator Agent"
	@echo "================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make run         - Run the backend server"
	@echo "  make dev         - Run backend in development mode"
	@echo "  make frontend    - Serve frontend on port 3000"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-run  - Run with Docker Compose"
	@echo "  make docker-stop - Stop Docker containers"
	@echo "  make clean       - Clean up generated files"
	@echo "  make test        - Run tests"
	@echo ""

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo ""
	@echo "✓ Installation complete!"
	@echo "  Don't forget to set your OPENAI_API_KEY in backend/.env"

# Run backend server
run:
	cd backend && . venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Run in development mode with auto-reload
dev:
	cd backend && . venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Serve frontend
frontend:
	cd frontend && npm run dev

# Build Docker images
docker-build:
	docker-compose build

# Run with Docker Compose
docker-run:
	docker-compose up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"

# Stop Docker containers
docker-stop:
	docker-compose down

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/venv 2>/dev/null || true
	rm -rf frontend/node_modules 2>/dev/null || true
	@echo "✓ Cleaned up generated files"

# Run tests
test:
	cd backend && . venv/bin/activate && python -m pytest tests/ -v

# Setup environment file
setup-env:
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "✓ Created backend/.env from template"; \
		echo "  Please edit and add your OPENAI_API_KEY"; \
	else \
		echo "backend/.env already exists"; \
	fi
