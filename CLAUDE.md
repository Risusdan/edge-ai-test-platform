# Edge AI Test Platform — Claude Guide

## Top Goal

**Learn by doing.** This project is a learning journey first, portfolio piece second. We move in baby steps — understand each concept before moving to the next. Speed is not a priority; comprehension is.

## Workflow

### Baby Steps Cycle

```
1. Implement a micro-step on a feature branch (with Claude's help)
2. Push & create PR by yourself
3. Claude reviews the PR (tailored feedback for learning)
4. Fix issues, ask questions, dig deeper
5. Write learning notes (in `notes/`)
6. Merge to main
7. Next micro-step
```

### Git Branching

- `main` — always working, merge via PR only
- Feature branches: `feat/a1a-project-init`, `feat/a1b-fastapi-health`, etc.
- One micro-step per branch/PR

### When I Ask for Help

- "wrap_up" — summarize what I just learned into clean notes
- "dig_deeper" — explain the underlying concepts in more detail
- "correct_me" — check my understanding and fix misconceptions

## Tech Stack

- Python 3.10+, uv (package manager)
- FastAPI, ONNX Runtime, Docker
- pytest, pytest-html
- OpenCV, Paramiko (later phases)

## Project Structure (target)

```
edge-ai-test-platform/
├── inference_service/     # FastAPI + ONNX model
├── tests/                 # unit / integration / e2e / failure_scenarios
├── docker/                # Dockerfile, docker-compose.yml
├── reports/               # Test reports
├── notes/                 # Learning notes per micro-step
├── docs/                  # Design decisions, assertion strategy
├── .github/workflows/     # CI/CD
├── pyproject.toml         # uv project config
└── CLAUDE.md              # This file
```

## Implementation Plan

Source plan: `./Edge-AI-Test-Platform-Plan.md`

## Code Style

- Keep it simple — no over-engineering
- Comments where logic isn't obvious
- Follow standard Python conventions (PEP 8)
