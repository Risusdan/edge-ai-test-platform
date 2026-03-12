# Edge AI Test Platform — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an industrial-grade Edge AI end-to-end test platform in 6 months, progressing from Docker-based simulation (Phase A) → Raspberry Pi HIL testing (Phase B) → full-stack monitoring system (Phase C), targeting SDET/System-Level Test Engineer roles at Google, NVIDIA, Qualcomm.

**Architecture:** Three-phase incremental build (A → B → C). Each phase delivers independently demonstrable results. Core differentiators: three-tier assertion strategy (Halt/Continue/Retry), HAL abstraction layer, webcam visual verification, and failure evidence capture system.

**Tech Stack:** Python 3.10+, uv, pytest, FastAPI, Docker, ONNX Runtime, OpenCV, Paramiko, Playwright, HTML + Chart.js, SQLite, GitHub Actions

**Source Spec:** [Edge-AI-Test-Platform-v2](Edge-AI-Test-Platform-v2.md)

---

## Table of Contents

- [Design Principles](#design-principles)
- [Phase A: Edge AI Test Framework (Month 1)](#phase-a-edge-ai-test-framework-month-1)
- [Phase B: Raspberry Pi HIL Test Platform (Month 2-3)](#phase-b-raspberry-pi-hil-test-platform-month-2-3)
- [Phase C: Full-Stack Monitoring & Test System (Month 4-6)](#phase-c-full-stack-monitoring--test-system-month-4-6)
- [Hardware Procurement](#hardware-procurement)
- [Interview Narrative](#interview-narrative)
- [Daily Time Budget](#daily-time-budget)

---

## Design Principles

These five principles drive every decision across all phases:

1. **Test completeness first** — Cover fault injection, edge cases, and stress tests beyond happy path
2. **README is a core deliverable** — Architecture diagrams, test result screenshots, design decision docs from day one
3. **Frontend stays simple** — HTML + Chart.js over React; invest saved time into test depth
4. **Document design decisions** — Every tech choice needs a "why" explanation (key interview differentiator)
5. **Industrial-grade test thinking** — Visual evidence (screenshots, recordings), severity-tiered assertions, real failure scenario coverage

---

## Phase A: Edge AI Test Framework (Month 1)

**Focus:** Test architecture design quality over feature completeness.

### Target Repo Structure

```
edge-ai-test-platform/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── inference_service/
│   ├── app.py                      # FastAPI inference API
│   └── model/                      # ONNX model files
├── tests/
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests (API layer)
│   ├── e2e/                        # End-to-end tests
│   └── failure_scenarios/          # ⭐ Failure scenario tests
├── reports/
├── .github/workflows/
│   └── ci.yml
├── docs/
│   ├── design_decisions.md         # ⭐ Design decisions (incl. HAL rationale)
│   └── assertion_strategy.md       # ⭐ Three-tier assertion strategy
├── conftest.py                     # ⭐ Halt/Retry marker definitions
├── pyproject.toml                  # uv project config & dependencies
├── uv.lock                         # uv lockfile
├── pytest.ini
└── README.md                       # ⭐ Serious from day one
```

### Tech Stack

| Category       | Tool                              |
| -------------- | --------------------------------- |
| Package mgmt   | uv (venv + dependency management) |
| Inference env  | Docker + ONNX Runtime             |
| Test framework | pytest + pytest-html              |
| API service    | FastAPI                           |
| API testing    | requests / httpx                  |
| CI/CD          | GitHub Actions                    |
| Language       | Python 3.10+                      |

### A-1: Docker Inference Service (Week 1)

- [ ] Init project with `uv init edge-ai-test-platform` and configure `pyproject.toml`
- [ ] Add core dependencies: `uv add fastapi uvicorn onnxruntime pillow`
- [ ] Add dev dependencies: `uv add --dev pytest pytest-html httpx`
- [ ] Set up `.gitignore` (include `.venv/`), `pytest.ini`
- [ ] Create `inference_service/app.py` — FastAPI app with health check endpoint (`/health`)
- [ ] Download a lightweight ONNX model (e.g., MobileNetV2) into `inference_service/model/`
- [ ] Implement `/predict` endpoint — accepts image, returns classification result
- [ ] Write `docker/Dockerfile` for the inference service (use `uv` inside container for reproducible installs)
- [ ] Write `docker/docker-compose.yml` to orchestrate the service
- [ ] Verify: `docker compose up` → service responds on `localhost:8000/health`
- [ ] Commit: `feat: add Docker-based inference service with FastAPI + ONNX Runtime`

### A-2: pytest Framework Foundation (Week 1-2)

- [ ] Set up `conftest.py` with base fixtures (API client, test image fixtures)
- [ ] Implement pytest fixtures for Docker service lifecycle (start/stop between test sessions)
- [ ] Write `tests/unit/test_model_loading.py` — model loads correctly, returns expected shape
- [ ] Write `tests/unit/test_preprocessing.py` — image preprocessing produces correct tensor shape
- [ ] Write `tests/unit/test_postprocessing.py` — postprocessing returns valid classification labels
- [ ] Run unit tests via `uv run pytest tests/unit/ -v`, verify all pass
- [ ] Commit: `feat: add pytest framework with unit tests for inference pipeline`

### A-3: Integration & E2E Tests (Week 2)

- [ ] Write `tests/integration/test_health_endpoint.py` — `/health` returns 200
- [ ] Write `tests/integration/test_predict_endpoint.py` — `/predict` with valid image returns valid result
- [ ] Write `tests/integration/test_predict_invalid.py` — `/predict` with invalid input returns proper error
- [ ] Write `tests/e2e/test_full_inference_pipeline.py` — image upload → prediction → validate result format and confidence range
- [ ] Run all tests with Docker service via `uv run pytest -v`, verify pass
- [ ] Commit: `feat: add integration and E2E tests for inference API`

### A-4: Three-Tier Assertion Architecture (Week 3) ⭐

Distinguish fatal errors, non-fatal warnings, and flaky conditions using pytest markers:

- [ ] Implement `@pytest.mark.halt` marker in `conftest.py` — fatal errors that stop the entire suite
  ```python
  # conftest.py
  def pytest_configure(config):
      config.addinivalue_line("markers", "halt: fatal error - stop entire suite")
      config.addinivalue_line("markers", "retry: auto-retry on flaky conditions")

  @pytest.hookimpl(tryfirst=True)
  def pytest_runtest_makereport(item, call):
      if call.excinfo and item.get_closest_marker("halt"):
          item.session.shouldfail = f"HALT: {item.name} failed — stopping suite"
  ```
- [ ] Implement `@pytest.mark.retry` marker — auto-retry for flaky conditions
  ```python
  # Use pytest-retry or custom implementation
  @pytest.fixture(autouse=True)
  def retry_on_marker(request):
      marker = request.node.get_closest_marker("retry")
      if marker:
          max_retries = marker.kwargs.get("max_retries", 3)
          delay = marker.kwargs.get("delay", 1)
          # retry logic
  ```
- [ ] Write test demonstrating `@pytest.mark.halt` — `test_inference_service_unreachable()`
- [ ] Write test demonstrating `@pytest.mark.retry` — `test_inference_under_network_jitter()`
- [ ] Write `docs/assertion_strategy.md` explaining the three-tier design rationale
- [ ] Run tests, verify halt stops suite, retry retries
- [ ] Commit: `feat: implement three-tier assertion architecture (Halt/Continue/Retry)`

### A-5: Failure Scenario Tests (Week 3) ⭐

- [ ] Write `tests/failure_scenarios/test_invalid_input.py` — non-image files, oversized files, empty payload
- [ ] Write `tests/failure_scenarios/test_model_timeout.py` — simulate slow inference, verify timeout handling
- [ ] Write `tests/failure_scenarios/test_corrupted_model.py` — corrupt model file, verify graceful error
- [ ] Write `tests/failure_scenarios/test_concurrent_requests.py` — concurrent stress test with threading/asyncio
- [ ] Write `tests/failure_scenarios/test_out_of_memory.py` — simulate memory pressure
- [ ] Run all failure scenario tests, verify correct error handling
- [ ] Commit: `feat: add failure scenario tests (5 categories)`

### A-6: CI/CD Pipeline & Reporting (Week 4)

- [ ] Write `.github/workflows/ci.yml`:
  - Install `uv` via `astral-sh/setup-uv` action
  - Run `uv sync` to install dependencies
  - Run `uv run pytest` with Docker service
- [ ] Configure `pytest-html` for HTML report generation into `reports/`
- [ ] Push to GitHub, verify CI pipeline runs and passes
- [ ] Commit: `feat: add GitHub Actions CI pipeline with pytest-html reports`

### A-7: Documentation — README v1 & Design Decisions (Week 4)

- [ ] Write `README.md` v1:
  - Project motivation & goals (3-4 sentences)
  - System architecture diagram (ASCII art or Mermaid)
  - Design decisions summary
  - Test strategy (test pyramid, failure scenario coverage)
  - Quick start (`uv sync && docker compose up`)
  - Test result screenshots
  - Known limitations & future plans
- [ ] Write `docs/design_decisions.md`:
  - Why uv (fast, reproducible, replaces pip + venv + pip-tools)
  - Why ONNX Runtime (portability across edge devices)
  - Why FastAPI (lightweight, Python-native, JD alignment)
  - Why pytest over unittest (fixture system, plugin ecosystem)
  - HAL layered design rationale (preview for Phase B)
- [ ] Capture test result screenshots, add to README
- [ ] Commit: `docs: add README v1, design decisions, and assertion strategy docs`

### Phase A Deliverables Checklist

- [ ] Docker inference service running and testable
- [ ] pytest framework with unit / integration / E2E tests
- [ ] Three-tier assertion architecture (Halt / Continue / Retry)
- [ ] 5 failure scenario test categories
- [ ] GitHub Actions CI pipeline with HTML reports
- [ ] README v1 with architecture diagram and design decisions
- [ ] `assertion_strategy.md` and `design_decisions.md`

---

## Phase B: Raspberry Pi HIL Test Platform (Month 2-3)

**Focus:** Cross-layer debugging capability demonstration.

### Target Repo Structure (additions)

```
edge-ai-test-platform/
├── ...（Phase A content）
├── plugins/
│   └── hal/                         # ⭐ HAL abstraction layer
│       ├── camera_hal.py
│       ├── ssh_hal.py
│       └── i2c_hal.py
├── device/
│   ├── setup/                       # Pi environment setup scripts
│   ├── deploy.sh                    # One-click deploy to Pi
│   └── health_check.py              # Device health check
├── tests/
│   ├── ...（Phase A content）
│   ├── hil/                         # HIL tests (incl. failure scenarios)
│   │   └── visual/                  # ⭐ Webcam visual verification
│   └── hardware/
│       ├── test_i2c_sensor.py
│       └── test_gpio.py
├── config/
│   └── device_config.yaml
└── docs/
    ├── design_decisions.md          # ⭐ Updated with HAL design
    ├── assertion_strategy.md
    └── hil_architecture.md
```

### Additional Tech Stack

| Category            | Tool                       |
| ------------------- | -------------------------- |
| Hardware platform   | Raspberry Pi 4/5           |
| Image input         | USB Camera + OpenCV        |
| Remote control      | Paramiko (SSH) / Fabric    |
| System monitoring   | psutil / vcgencmd          |
| I2C communication   | smbus2 / i2c-tools         |
| Visual verification | OpenCV + pytest-image-diff |

### B-1: Hardware Procurement & Pi Setup (Month 2, Week 1)

- [ ] Purchase hardware (see [Hardware Procurement](#hardware-procurement) section)
- [ ] Install Raspberry Pi OS (64-bit recommended)
- [ ] Configure SSH access with key-based authentication
- [ ] Install Docker on Pi
- [ ] Deploy Phase A inference service to Pi using `device/deploy.sh`
- [ ] Write `device/setup/` scripts for reproducible Pi environment
- [ ] Write `device/health_check.py` — check SSH connectivity, Docker status, disk space, temperature
- [ ] Verify: inference service runs on Pi, responds to API calls from dev machine
- [ ] Commit: `feat: add Pi setup scripts and one-click deployment`

### B-2: HAL Abstraction Layer (Month 2, Week 2) ⭐

- [ ] Add HAL dependencies: `uv add paramiko opencv-python smbus2`
- [ ] Design HAL interface pattern — each HAL module exposes a consistent interface
- [ ] Implement `plugins/hal/ssh_hal.py`:
  - `connect()`, `execute_command()`, `upload_file()`, `download_file()`, `disconnect()`
  - Wraps Paramiko with retry logic and connection pooling
- [ ] Implement `plugins/hal/camera_hal.py`:
  - `capture_frame()`, `capture_screenshot()`, `start_recording()`, `stop_recording()`
  - Wraps OpenCV VideoCapture
- [ ] Implement `plugins/hal/i2c_hal.py`:
  - `read_sensor()`, `write_register()`, `scan_bus()`
  - Wraps smbus2
- [ ] Write unit tests for each HAL module (mock hardware interfaces)
- [ ] Update `docs/design_decisions.md` with HAL design rationale:
  > When hardware changes (e.g., Pi → Jetson), only HAL layer needs modification. All test logic remains untouched.
- [ ] Commit: `feat: implement HAL abstraction layer (camera, SSH, I2C)`

### B-3: Remote Test Control & Basic HIL Tests (Month 2, Week 2-3)

- [ ] Create pytest fixtures for remote device connection (using `ssh_hal`)
- [ ] Write `tests/hil/test_normal_inference.py` — inject image via SSH → trigger inference → validate result
- [ ] Write `tests/hil/test_system_resources.py` — monitor CPU, memory, temperature during inference
- [ ] Write `config/device_config.yaml` — device IP, SSH credentials, paths
- [ ] Run HIL tests from dev machine against Pi, verify pass
- [ ] Commit: `feat: add remote test framework and basic HIL tests`

### B-4: HIL Failure Scenario Tests (Month 2, Week 4 — Month 3, Week 2) ⭐

- [ ] Write `tests/hil/test_camera_failure.py` — simulate camera disconnect (stop capture service)
- [ ] Write `tests/hil/test_network_disconnect.py` — test behavior during network interruption
- [ ] Write `tests/hil/test_thermal_throttling.py` — stress CPU, monitor inference degradation under thermal throttling
- [ ] Write `tests/hil/test_resource_exhaustion.py` — fill memory/CPU, verify graceful degradation
- [ ] Write `tests/hil/test_recovery_behavior.py` — verify automatic recovery after fault injection
- [ ] Run all HIL failure tests, verify correct fault handling
- [ ] Commit: `feat: add HIL failure scenario tests (5 categories)`

### B-5: Webcam Visual Verification (Month 3, Week 1-2) ⭐

- [ ] Add visual test dependencies: `uv add --dev pytest-image-diff`
- [ ] Write `tests/hil/visual/test_visual_led_detection.py`:
  - Use OpenCV to detect LED state (on/off/blinking) from webcam feed
  - `camera_hal.capture_frame()` → color detection → state assertion
- [ ] Write `tests/hil/visual/test_screen_capture.py`:
  - Capture inference result display → save screenshot
  - Compare against expected baseline
- [ ] Write `tests/hil/visual/test_visual_regression.py`:
  - Pixel-diff comparison against baseline screenshots
  - Threshold-based pass/fail (allow minor variance)
- [ ] Create pytest fixtures for visual test setup/teardown (camera init, baseline management)
- [ ] Run visual tests, verify LED detection and screenshot capture work
- [ ] Commit: `feat: add webcam visual verification layer (LED, screenshots, regression)`

### B-6: I2C Sensor Integration (Month 3, Week 2)

- [ ] Connect BME280 (or similar) sensor to Pi via I2C
- [ ] Write `tests/hardware/test_i2c_sensor.py` — read temperature, humidity, verify reasonable range
- [ ] Write `tests/hardware/test_gpio.py` — basic GPIO read/write verification
- [ ] Run hardware tests on Pi, verify sensor readings
- [ ] Commit: `feat: add I2C sensor and GPIO hardware tests`

### B-7: CI Pipeline Update & Documentation (Month 3, Week 3)

- [ ] Update `.github/workflows/ci.yml` to support remote device test trigger (conditional workflow)
- [ ] Write `docs/hil_architecture.md`:
  - HIL architecture diagram
  - HAL layer design explanation
  - Visual verification workflow
  - Failure scenario coverage matrix
- [ ] Update README with HIL test results, visual verification demo screenshots
- [ ] Commit: `docs: add HIL architecture docs and update README`

### B-8: Technical Blog Post #1 (Month 3, Week 3-4)

- [ ] Draft English blog post:
  - Title: "How I Built a Hardware-in-the-Loop Test Platform for Edge AI Devices"
  - Platform: Medium or Dev.to
  - Cover: motivation, architecture, key challenges, lessons learned
- [ ] Review and polish draft
- [ ] Publish blog post
- [ ] Add blog link to README
- [ ] Commit: `docs: add blog post link to README`

### Phase B Deliverables Checklist

- [ ] Inference service running on Raspberry Pi
- [ ] HAL abstraction layer (camera, SSH, I2C)
- [ ] Remote test execution from dev machine
- [ ] 5 HIL failure scenario tests
- [ ] Webcam visual verification (LED detection, screenshots, regression)
- [ ] I2C sensor integration
- [ ] `hil_architecture.md` with diagrams
- [ ] English technical blog post published
- [ ] Updated README with HIL demo

---

## Phase C: Full-Stack Monitoring & Test System (Month 4-6)

**Focus:** System integration capability and test completeness.

### Target Repo Structure (additions)

```
edge-ai-test-platform/
├── ...（Phase A + B content）
├── server/
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── models/
│   ├── db/
│   │   └── schema.sql
│   └── Dockerfile
├── dashboard/
│   ├── index.html               # HTML + Chart.js (not React)
│   └── Dockerfile
├── reports/
│   ├── test_report.html         # pytest-html (with failure screenshots)
│   └── evidence/                # ⭐ Screenshot & video evidence
│       ├── screenshots/
│       └── recordings/
├── tests/
│   ├── ...（Phase A + B content）
│   └── web/
│       ├── test_dashboard_ui.py     # Playwright tests
│       └── test_api_endpoints.py
├── docker-compose.yml
└── docs/
    ├── design_decisions.md
    ├── assertion_strategy.md
    ├── hil_architecture.md
    ├── api_spec.md
    └── system_architecture.md      # ⭐ Complete system architecture
```

### Additional Tech Stack

| Category       | Tool            | Rationale                                           |
| -------------- | --------------- | --------------------------------------------------- |
| Backend API    | FastAPI         | Lightweight, Python-native, JD alignment            |
| Frontend UI    | HTML + Chart.js | Fast to build, avoid React learning cost            |
| Web automation | Playwright      | Modern web testing standard                         |
| Data storage   | SQLite          | Simple, no extra service, upgradeable to PostgreSQL |
| Deployment     | Docker Compose  | Multi-service orchestration, one-click start        |

### C-1: FastAPI Backend (Month 4, Week 1-2)

- [ ] Design API endpoints:
  - `GET /devices` — list registered devices
  - `GET /devices/{id}/status` — device health status
  - `POST /devices/{id}/test` — trigger test run
  - `GET /tests` — list test results
  - `GET /tests/{id}` — get test result detail
- [ ] Write `server/db/schema.sql` — devices table, test_results table, test_evidence table
- [ ] Implement SQLite database layer with connection management
- [ ] Implement `server/api/main.py` with FastAPI app
- [ ] Implement `server/api/routes/` — devices, tests, health routes
- [ ] Implement `server/api/models/` — Pydantic models for request/response
- [ ] Write `tests/web/test_api_endpoints.py` — test all API endpoints
- [ ] Write `server/Dockerfile`
- [ ] Write `docs/api_spec.md` — API documentation
- [ ] Commit: `feat: add FastAPI backend with device management and test APIs`

### C-2: Failure Evidence Capture System (Month 4, Week 3-4) ⭐

- [ ] Implement auto-screenshot hook in `conftest.py`:
  ```python
  @pytest.hookimpl(tryfirst=True, hookwrapper=True)
  def pytest_runtest_makereport(item, call):
      outcome = yield
      report = outcome.get_result()
      if report.when == "call" and report.failed:
          screenshot_path = capture_screenshot(item.name)
          attach_to_report(report, screenshot_path)
  ```
- [ ] Implement `capture_screenshot()` — save to `reports/evidence/screenshots/`
- [ ] Implement `attach_to_report()` — embed screenshot in pytest-html report
- [ ] Add video recording capability for critical test nodes — save to `reports/evidence/recordings/`
- [ ] Write test to verify: when a test fails, screenshot is captured and appears in HTML report
- [ ] Commit: `feat: add failure auto-screenshot and evidence capture system`

### C-3: Web Dashboard (Month 5, Week 1-2)

- [ ] Create `dashboard/index.html`:
  - Device list with status indicators (online/offline/error)
  - Test result history table
  - Chart.js trend charts (pass rate over time, inference latency)
  - Test trigger button per device
- [ ] Implement JavaScript to fetch data from FastAPI endpoints
- [ ] Write `dashboard/Dockerfile` (simple nginx serve)
- [ ] Verify: dashboard loads, shows device data, charts render
- [ ] Commit: `feat: add web dashboard with Chart.js visualizations`

### C-4: Playwright Web UI Tests (Month 5, Week 3)

- [ ] Add Playwright dependency: `uv add --dev playwright` and run `uv run playwright install`
- [ ] Write `tests/web/test_dashboard_ui.py`:
  - Page loads successfully
  - Device list renders
  - Test trigger button works
  - Charts display data
  - Responsive layout check
- [ ] Integrate Playwright screenshots on failure (connects to evidence system)
- [ ] Run Playwright tests, verify pass
- [ ] Commit: `feat: add Playwright web UI automation tests`

### C-5: Docker Compose Integration (Month 5, Week 4)

- [ ] Write `docker-compose.yml` orchestrating:
  - Inference service
  - FastAPI backend
  - Dashboard (nginx)
  - (Optional) test runner service
- [ ] Verify: `docker compose up` starts entire system
- [ ] Write integration test for full system (device registers → test triggers → results display)
- [ ] Commit: `feat: add Docker Compose for full system orchestration`

### C-6: Final Documentation & Polish (Month 6, Week 1-2)

- [ ] Write `docs/system_architecture.md`:
  - Complete system architecture diagram (all three phases)
  - Data flow diagram
  - Component interaction diagram
  - Deployment topology
- [ ] Update `docs/design_decisions.md` with Phase C decisions:
  - Why HTML + Chart.js over React
  - Why SQLite (with upgrade path)
  - Evidence capture design rationale
- [ ] Comprehensive test coverage review — identify and fill gaps
- [ ] Update README to final version:
  - Demo GIF or screenshots of full system
  - Complete architecture diagram
  - All design decisions summarized
  - Full quick-start guide (`uv sync && docker compose up`)

### C-7: Technical Blog Post #2 (Month 6, Week 3-4)

- [ ] Draft English blog post:
  - Title: "Building an Industrial-Grade AIoT Test & Monitoring Platform"
  - Cover: full system architecture, three-tier assertion, evidence capture, lessons learned
- [ ] Review and polish draft
- [ ] Publish blog post
- [ ] Add blog link to README
- [ ] Commit: `docs: final README, system architecture, blog post #2`

### C-8: Optional Stretch Goals (Month 6, remaining time)

- [ ] NVIDIA Jetson Nano support (directly aligns with NVIDIA JD)
- [ ] Multi-device management (second Pi)
- [ ] RTSP stream simulation

### Phase C Deliverables Checklist

- [ ] FastAPI backend with device management and test APIs
- [ ] Failure evidence capture system (auto-screenshot + video)
- [ ] Web dashboard with Chart.js visualizations
- [ ] Playwright web UI automation tests
- [ ] Docker Compose one-click deployment
- [ ] `system_architecture.md` with complete diagrams
- [ ] `api_spec.md`
- [ ] English technical blog post #2 published
- [ ] Final README with demo GIF/screenshots

---

## Hardware Procurement

### Phase B Required (purchase at end of Month 1)

| Item                         | Est. Price (NTD)   |
| ---------------------------- | ------------------ |
| Raspberry Pi 4 (4GB) or Pi 5 | 1,800 - 3,000      |
| USB Webcam                   | 300 - 800          |
| MicroSD Card (32GB+)         | 200 - 400          |
| I2C Sensor (e.g., BME280)    | 100 - 200          |
| Dupont wires + Breadboard    | 100 - 200          |
| USB-C Power Supply           | 200 - 400          |
| **Subtotal**                 | **~2,700 - 5,000** |

### Phase C Optional

| Item                | Est. Price (NTD) | Purpose                         |
| ------------------- | ---------------- | ------------------------------- |
| Second Raspberry Pi | 1,800 - 3,000    | Multi-device management testing |
| NVIDIA Jetson Nano  | 3,000 - 5,000    | Direct NVIDIA JD alignment      |

---

## Interview Narrative

### Chinese (preparation)

> 「我花了六個月建構了一個工業級 Edge AI 裝置端到端測試平台。從 Docker 化的推論服務測試開始，我設計了三層斷言架構——區分致命錯誤立即停止、非致命錯誤繼續跑、不穩定環境自動重試，這是真實工業測試系統的標準設計。之後擴展到 Raspberry Pi 上的 HIL 測試，加入 Webcam 視覺驗證層，能自動辨識 LED 狀態並在測試失敗時截圖存證。最終整合成包含 Web Dashboard、API Server、自動化報告（含失敗截圖）的完整系統。整個過程讓我從硬體層、Embedded Linux 層、到應用層，建立了跨層級的除錯與測試設計能力。」

### English (interview)

> "I spent six months building an industrial-grade end-to-end test platform for Edge AI devices. I started by designing a three-tier assertion architecture — distinguishing fatal errors that halt the suite, non-fatal ones that continue, and flaky conditions that trigger automatic retries. I then expanded to a Hardware-in-the-Loop setup on Raspberry Pi, adding a visual verification layer using OpenCV to detect LED states and automatically capture screenshots on test failures. Finally, I integrated everything into a full system with a Web Dashboard, API server, and automated HTML reports that include failure screenshots and video evidence. This gave me hands-on experience designing test systems across hardware, Embedded Linux, and application layers."

---

## Daily Time Budget

| Day type  | Time           | Notes                              |
| --------- | -------------- | ---------------------------------- |
| Weekday   | 30-45 min      | Sustainable pace, avoid burnout    |
| Weekend   | 1.5-2 hours    | Tackle larger tasks                |
| **Total** | **~200 hours** | 6 months to complete full platform |

---

## Timeline Overview

```
Month 1    ████████████  Phase A: pytest + CI/CD + Docker + failure scenarios + 3-tier assertions
Month 2    ████████████  Phase B early: hardware procurement + Pi setup + HAL + basic HIL tests
Month 3    ████████████  Phase B late: HIL failure scenarios + visual verification + I2C + blog #1
Month 4    ████████████  Phase C early: FastAPI backend + database + evidence capture system
Month 5    ████████████  Phase C mid: Web dashboard + Playwright tests + Docker Compose
Month 6    ████████████  Phase C late: documentation + test coverage review + blog #2
```

---
up:: [Edge-AI-Test-Platform-v2](Edge-AI-Test-Platform-v2.md)
#type/decision #source/self-study #status/seed
