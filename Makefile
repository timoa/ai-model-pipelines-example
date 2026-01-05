.PHONY: help build test train clean docker-build docker-push k8s-deploy

help:
	@echo "AI Research Platform - Makefile Commands"
	@echo ""
	@echo "Build & Test:"
	@echo "  make build          - Build all Bazel targets"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run code quality checks"
	@echo ""
	@echo "Training:"
	@echo "  make train-smoke    - Run smoke test training"
	@echo "  make train-small    - Run small model training"
	@echo ""
	@echo "Data Pipeline:"
	@echo "  make data-download  - Download dataset"
	@echo "  make data-tokenize  - Tokenize dataset"
	@echo "  make data-split     - Split train/val"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build all Docker images"
	@echo "  make docker-push    - Push images to registry"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-deploy     - Deploy training job"
	@echo "  make k8s-logs       - View training logs"
	@echo "  make k8s-clean      - Clean up resources"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make format         - Format code with Black"

build:
	bazel build //...

test:
	bazel test //...

lint:
	black --check src/
	ruff check src/
	mypy src/ --ignore-missing-imports

format:
	black src/
	ruff check --fix src/

train-smoke:
	python src/train.py --config configs/smoke-test.yaml

train-small:
	python src/train.py --config configs/train-small.yaml

data-download:
	python scripts/download_data.py --dataset openwebtext --output-dir data/raw

data-tokenize:
	python scripts/tokenize_data.py --input-dir data/raw --output-dir data/tokenized --tokenizer gpt2

data-split:
	python scripts/split_data.py --input-dir data/tokenized --train-dir data/train --val-dir data/val

docker-build:
	docker build -f docker/base/Dockerfile -t ai-research-platform-base:latest .
	docker build -f docker/training/Dockerfile -t ai-research-platform-training:latest .
	docker build -f docker/inference/Dockerfile -t ai-research-platform-inference:latest .

docker-push:
	docker push ai-research-platform-base:latest
	docker push ai-research-platform-training:latest
	docker push ai-research-platform-inference:latest

k8s-deploy:
	kubectl create namespace ai-research --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f k8s/training-job.yaml

k8s-logs:
	kubectl logs -f job/gpt-training -n ai-research

k8s-clean:
	kubectl delete -f k8s/training-job.yaml

clean:
	bazel clean
	rm -rf outputs/
	rm -rf data/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
