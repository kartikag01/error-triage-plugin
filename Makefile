PY ?= python

setup:            ## install dependencies
	$(PY) -m pip install -r requirements.txt

service:          ## run the triage microservice on :8000
	$(PY) -m uvicorn triage_service.main:app --port 8000

seed:             ## load synthetic errors (re-run any time; --reset wipes first)
	$(PY) scripts/seed.py --reset

data:             ## regenerate data/errors.jsonl
	$(PY) data/generate_errors.py

test:
	$(PY) -m pytest -q

.PHONY: setup service seed data test
