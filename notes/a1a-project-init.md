# A-1a: Project Init with uv

## What I did

- Created a GitHub repo (`edge-ai-test-platform`) with `gh repo create`
- Ran `uv init` to set up the Python project
- Customized `pyproject.toml` with project description and pytest config
- Added core deps: `uv add fastapi uvicorn onnxruntime pillow`
- Added dev deps: `uv add --dev pytest pytest-html httpx`
- Created folder structure: `inference_service/`, `tests/`, `docs/`, `notes/`, `reports/`
- Removed the placeholder `main.py`

## Key Concepts

### What is uv?

**One-sentence:** uv is an all-in-one Python project manager — it replaces `pip`, `venv`, `pip-tools`, and even `pyenv` in a single tool.

**Why it exists:** In traditional Python, you need multiple tools that don't talk to each other well:
- `pyenv` → manage Python versions
- `python -m venv` → create virtual environments
- `pip` → install packages
- `pip-tools` / `pip freeze` → lock dependency versions

That's 4 tools for one job. uv does all of it, and it's written in Rust so it's ~10-100x faster than pip.

**How it works (mental model):** Think of uv like a restaurant kitchen manager. It:
1. Picks the right chef (Python version) → `.python-version`
2. Sets up a clean kitchen (virtual environment) → `.venv/`
3. Reads the recipe (your dependencies) → `pyproject.toml`
4. Locks in exact ingredient brands (pinned versions) → `uv.lock`
5. Stocks the kitchen (installs everything) → `uv sync`

### pyproject.toml

The "recipe card" for your project. It tells uv (and other tools):
- Project name, version, description
- What Python version is needed
- What packages to install
- Tool configs (like pytest settings)

### uv.lock

A snapshot of the **exact versions** of every package installed, including sub-dependencies. This guarantees that anyone running `uv sync` gets the identical environment. You commit this file to git.

### .venv/

A folder containing a copy of Python + all installed packages, isolated from your system Python. This way each project can have different package versions without conflicts. It's gitignored because it can be recreated with `uv sync`.

### Dev dependencies vs regular dependencies (deep dive)

Imagine you're shipping a product (a lunchbox). The food inside is what the customer needs (`dependencies`). The knife you used to cut the food stays in your kitchen (`dev-dependencies`). You don't ship the knife.

Without this separation, everyone who installs your app would also download pytest, linters, test tools — stuff they'll never use. That wastes time, disk space, and can even introduce security risks.

In `pyproject.toml`, they live in two separate sections:

| Section                   | What goes here                        | When it's installed                                          |
| ------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| `dependencies`            | fastapi, onnxruntime, pillow, uvicorn | **Always** — anyone who uses your app gets these             |
| `[dependency-groups] dev` | pytest, pytest-html, httpx            | **Only during development** — when you're coding and testing |

Real example from our project:
- Docker container running inference in production → needs `fastapi` and `onnxruntime`. Does **not** need `pytest`.
- You sitting at your laptop writing tests → needs `pytest` and `httpx`. These stay on your machine.

Later in the Dockerfile (A-1d), we'll use `uv sync --no-dev` to skip dev deps in production.

## Commands Learned

| Command              | What it does                                                                           |
| -------------------- | -------------------------------------------------------------------------------------- |
| `uv init`            | Create a new Python project (generates `pyproject.toml`, `.python-version`, `main.py`) |
| `uv add <pkg>`       | Add a production dependency and install it                                             |
| `uv add --dev <pkg>` | Add a dev-only dependency                                                              |
| `uv sync`            | Install all dependencies from `uv.lock` (use this to set up on a new machine)          |
| `uv sync --no-dev`   | Install only production dependencies (for Docker/production)                           |
| `uv run <cmd>`       | Run a command inside the virtual environment (e.g., `uv run pytest`)                   |

## Gotchas

- `uv init` creates a `main.py` placeholder — delete it if you don't need it
- `.venv/` should be in `.gitignore` (we already handled this)
- `uv.lock` **should** be committed — it's how others reproduce your exact environment

## Questions for Later

- How does `uv` compare to `poetry`? (another popular Python project manager)
- What happens when two dependencies need conflicting versions of the same sub-dependency?
- How does `uv` work inside Docker? (we'll hit this in A-1d)
- What is PEP 735 (the spec behind `[dependency-groups]`)?
