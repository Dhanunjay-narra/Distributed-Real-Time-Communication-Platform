.PHONY: help install test lint run
help:
	@echo "Chatbot Distributed Platform"
test:
	pytest tests/ -v
lint:
	python -m flake8 packages services tests || true
