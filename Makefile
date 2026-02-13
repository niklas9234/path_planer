# Monorepo Makefile
# Usage: make <target>
# Targets are intentionally simple and shell-friendly.

SHELL := /bin/bash

PYTHON ?= python3
PIP ?= pip3

BACKEND_DIR := backend
CORE_DIR := core
FRONTEND_DIR := frontend

# If you use a venv, set VENV=.venv and call `make venv`
VENV ?= .venv
VENV_BIN := $(VENV)/bin
VENV_PY := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

# Prefer venv python if present
ifeq ($(wildcard $(VENV_PY)),)
PY := $(PYTHON)
PIP_CMD := $(PIP)
else
PY := $(VENV_PY)
PIP_CMD := $(VENV_PIP)
endif

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo ""
	@echo "  Setup:"
	@echo "    make venv              Create local Python venv ($(VENV))"
	@echo "    make install           Install Python dev dependencies (black, ruff, pytest, mypy, pre-commit)"
	@echo ""
	@echo "  Run:"
	@echo "    make backend-run       Run backend server (main.py in backend/)"
	@echo "    make frontend-run      Run frontend dev server"
	@echo "    make dev               Ruun both backend and frontend"
	@echo ""
	@echo "  Quality:"
	@echo "    make format            Format Python (black) and auto-fix lint (ruff)"
	@echo "    make lint              Lint Python (ruff) without fixing"
	@echo "    make typecheck         Run mypy "
	@echo "    make test              Run Python tests (pytest)"
	@echo ""
	@echo "  Frontend (optional, if set up):"
	@echo "    make frontend-install  npm install in frontend/"
	@echo "    make frontend-lint     npm run lint in frontend/"
	@echo "    make frontend-format   npm run format in frontend/"
	@echo "    make frontend-test     npm test in frontend/"
	@echo ""

.PHONY: venv
venv:
	@$(PYTHON) -m venv $(VENV)
	@echo "Created venv at $(VENV)"
	@echo "Activate: source $(VENV)/bin/activate"

.PHONY: install
install:
	@$(PIP_CMD) install -U pip
	@$(PIP_CMD) install black ruff pytest mypy pre-commit
	@echo "Installed Python dev tools."

# --- Run targets ---

.PHONY: backend-run
backend-run:
	@echo "Starting backend..."
	@$(PY) -m backend.main

.PHONY: frontend-run
frontend-run:
	@echo "Starting frontend..."
	@cd $(FRONTEND_DIR) && npm run dev

.PHONY: dev
dev:
	@echo "Run in two terminals:"
	@echo "  Terminal 1: make backend-run"
	@echo "  Terminal 2: make frontend-run"

# --- Quality targets (Python) ---

.PHONY: format
format:
	@echo "Formatting (black) ..."
	@$(PY) -m black $(BACKEND_DIR) $(CORE_DIR)
	@echo "Lint-fix (ruff) ..."
	@$(PY) -m ruff check $(BACKEND_DIR) $(CORE_DIR) --fix

.PHONY: lint
lint:
	@$(PY) -m ruff check $(BACKEND_DIR) $(CORE_DIR)

.PHONY: typecheck
typecheck:
	@$(PY) -m mypy $(BACKEND_DIR) $(CORE_DIR)

.PHONY: test
test:
	@$(PY) -m pytest -q

# --- Frontend convenience targets ---

.PHONY: frontend-install
frontend-install:
	@cd $(FRONTEND_DIR) && npm install

.PHONY: frontend-lint
frontend-lint:
	@cd $(FRONTEND_DIR) && npm run lint

.PHONY: frontend-format
frontend-format:
	@cd $(FRONTEND_DIR) && npm run format

.PHONY: frontend-test
frontend-test:
	@cd $(FRONTEND_DIR) && npm test
