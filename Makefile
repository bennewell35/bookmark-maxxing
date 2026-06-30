SHELL := /bin/bash

# Pinned local model name (see Modelfile / docker-compose.yml).
MODEL ?= bookmark-maxxing
FIXTURE ?= tests/fixtures/x_mcp_bookmarks.json
INPUT ?= /tmp/bm.json
PROMPT ?= extract-skills
CLI ?= PYTHONPATH=src python3 -m bookmark_maxxing.cli
SMOKE_INPUT ?= /tmp/bookmark-maxxing-smoke.json

.PHONY: help install test smoke lint model model-down ingest extract summaries demo

help:
	@echo "Targets:"
	@echo "  install     editable install into ./.venv"
	@echo "  test        run the unit suite + compile/whitespace checks"
	@echo "  smoke       run the offline MCP ingest/extract CLI path"
	@echo "  model       start the Ollama container and build the pinned '$(MODEL)' model"
	@echo "  model-down  stop the Ollama container"
	@echo "  ingest      ingest the fixture bookmarks -> $(INPUT)"
	@echo "  extract     compose-only extract ($(PROMPT)) from $(INPUT)"
	@echo "  summaries   LLM summaries of bookmarks via the pinned model"
	@echo "  demo        ingest -> LLM skills via the pinned model"

install:
	python3 -m venv .venv
	./.venv/bin/pip install -e .

test:
	PYTHONPATH=src python3 -m unittest discover -s tests
	python3 -m compileall -q src tests
	git diff --check
	$(MAKE) smoke

smoke:
	$(CLI) ingest-x --mcp --input $(FIXTURE) --format json > $(SMOKE_INPUT)
	$(CLI) extract --input $(SMOKE_INPUT) --prompt read-bookmarks > /dev/null

# Bring up Ollama in Docker and build the pinned model from the Modelfile.
# Downloads the small base model on first run (no weights committed to git).
model:
	docker compose up -d ollama
	@echo "waiting for ollama..."
	@until docker compose exec -T ollama ollama list >/dev/null 2>&1; do sleep 2; done
	docker compose exec -T ollama ollama create $(MODEL) -f /Modelfile
	@echo "Model '$(MODEL)' ready at http://localhost:11434/v1"

model-down:
	docker compose down

ingest:
	$(CLI) ingest-x --mcp --input $(FIXTURE) --format json > $(INPUT)
	@echo "wrote $(INPUT)"

extract: ingest
	$(CLI) extract --input $(INPUT) --prompt $(PROMPT)

summaries: ingest
	BOOKMARK_MAXXING_LLM_MODEL=$(MODEL) $(CLI) extract --input $(INPUT) --prompt read-bookmarks --llm

demo: ingest
	BOOKMARK_MAXXING_LLM_MODEL=$(MODEL) $(CLI) extract --input $(INPUT) --prompt extract-skills --llm
