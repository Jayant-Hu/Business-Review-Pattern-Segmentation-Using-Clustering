.PHONY: install pipeline run test lint docker-up docker-down clean

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

pipeline:
	python scripts/run_pipeline.py --step all

run:
	streamlit run app.py

test:
	pytest tests/ --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/
	black --check src/ tests/

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
