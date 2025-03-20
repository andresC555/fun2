.PHONY: setup test lint format run-service run-all clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup              - Set up development environment"
	@echo "  make test [SERVICE=...] - Run tests (for all or specific service)"
	@echo "  make lint [SERVICE=...] - Run linters (for all or specific service)"
	@echo "  make format             - Format code with Black and isort"
	@echo "  make run-service SERVICE=... - Run a specific service"
	@echo "  make run-all            - Run all services with Docker Compose"
	@echo "  make clean              - Clean build artifacts"

# Set up development environment
setup:
	@echo "Setting up development environment..."
	@./pants --version > /dev/null || curl -L -O https://github.com/pantsbuild/pants/releases/download/release_2.15.0/pants && chmod +x ./pants
	@python -m pip install --upgrade pip
	@python -m pip install pre-commit
	@pre-commit install

# Run tests
test:
ifdef SERVICE
	@echo "Running tests for $(SERVICE)..."
	@./pants test services/$(SERVICE)/tests::
else
	@echo "Running all tests..."
	@./pants test ::
endif

# Run linters
lint:
ifdef SERVICE
	@echo "Linting $(SERVICE)..."
	@./pants lint services/$(SERVICE)::
else
	@echo "Linting all code..."
	@./pants lint ::
endif

# Format code
format:
	@echo "Formatting code..."
	@./pants fmt ::

# Run a specific service
run-service:
ifndef SERVICE
	$(error SERVICE is not set. Use make run-service SERVICE=<service_name>)
endif
	@echo "Running $(SERVICE)..."
	@./pants run services/$(SERVICE)/src:server

# Run all services with Docker Compose
run-all:
	@echo "Running all services with Docker Compose..."
	@docker-compose up

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@./pants clean-all
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
