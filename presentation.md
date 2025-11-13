---
title: Automation Build & Test Tracker
theme: default
paginate: true
marp: true
---

# 🧩 Automation Build & Test Tracker
A configurable, multi-team tracker for Build → Test → Deploy

- Author: Venkata Gunasekhar V
- Stack: Django · DRF · PostgreSQL · (Celery/Redis optional)
- CI/CD: Jenkins or GitHub Actions
- Containerization: Docker (optional)

---

## 🎯 Motivation

- Fragmented Jenkins jobs and manual DoD checks
- Multiple teams contributing to one release flow
- No unified, weighted progress or trend metrics

Outcome:
- One source of truth for pipelines and runs
- Configurable JSON drives structure and ownership
- APIs + GUI for dashboards and integrations

---

## 🏗️ Architecture Overview

- Django + DRF backend (REST APIs, GUI views)
- PostgreSQL (SQLite for dev)
- Optional: Celery + Redis for async auto-checks
- Jenkins/GitHub Actions triggers → Run creation/updates

Supports:
- Webhooks & polling
- Grafana/Plotly-ready endpoints

---

## 🧱 Domain Model

- Organization → Team → Project → Pipeline
- Pipeline → Stage → SubStage
- Run → StageResult → SubStageResult
- Ownership: owner_team on Stage/SubStage

Benefits:
- Clear accountability by team
- Cross-team aggregation in one pipeline
- Consistent DoD tracking

---

## 🔧 JSON-Driven Configuration

- Configs in configs/*.json
- Define pipeline, stages, substages, weights, DoD, owner_team
- Loader creates/updates DB structure safely

Snippet:
```json
{
  "organization": "Mobile Org",
  "team": "Mobile Team",
  "project": "Mobile Project",
  "pipeline_name": "Mobile App Pipeline",
  "stages": [
    {
      "name": "Build", "weight": 0.5, "owner_team": "Build Automation",
      "substages": [
        {"name": "Compile", "weight": 0.6, "type":"auto", "endpoint":"/api/checks/compile/", "owner_team":"Build Automation"},
        {"name": "Sign", "weight": 0.4, "type":"manual", "owner_team":"Build Automation"}
      ]
    },
    {
      "name": "Test", "weight": 0.5, "owner_team": "Validation",
      "substages": [
        {"name": "Unit Tests", "weight": 0.5, "type":"auto", "owner_team":"Validation"},
        {"name": "Integration Tests", "weight": 0.5, "type":"manual", "owner_team":"Validation"}
      ]
    }
  ]
}
```

---

## 📊 Scoring Logic

- SubStage completion: 0–100
- Stage completion: weighted mean of substages (weights normalized)
- Overall score: weighted mean of stages (normalized)
- Recomputed on substage updates

Results:
- Comparable scores across runs and pipelines
- Robust to imperfect weight sums

---

## 🔌 APIs

- POST /api/runs/ → Create run
- POST /api/runs/{id}/update_stage/ → Update substage result
- GET /api/runs/{id}/summary/ → Hierarchical run breakdown
- GET /api/pipelines/{id}/trend/?n=10 → Last N runs trend
- GET /api/pipelines/{id}/ → Pipeline detail (ownership included)

Curl examples:
```bash
curl -X POST http://127.0.0.1:8000/api/runs/ -H "Content-Type: application/json" -d '{"pipeline_id": 1}'
curl http://127.0.0.1:8000/api/runs/1/summary/
```

---

## 🖥️ GUI (Built-in)

- / → Pipeline list
- /pipelines/<id>/ → Dashboard:
  - Overall score + latest run
  - Build/Test/Deploy sections
  - Owner team labels and progress bars
  - Substage table with status

Purpose:
- Demo ready
- Basis for future React/Grafana dashboards

---

## 🚀 Demo Plan

1) Load configs (multi-team):
```bash
for f in configs/*.json; do python manage.py load_pipeline_config "$f"; done
```
2) Create a run, simulate progress:
```bash
python manage.py simulate_run 1
```
3) Show GUI and APIs:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/api/pipelines/1/trend/?n=10
- http://127.0.0.1:8000/api/runs/1/summary/
4) Edit JSON (add a substage/team), reload, refresh

---

## 🛡️ Ownership & Access

- Stage/SubStage.owner_team for accountability
- Future: Filter APIs by team; RBAC to restrict updates to owned substages
- Audit fields (created/updated) can be added

---

## 🧭 Roadmap

- Async auto-validation via Celery (call auto_check_endpoint)
- Auth, RBAC, and audit logs
- OpenAPI/Swagger docs
- Unit tests for loader, scoring, signals
- Export to Grafana/Plotly

---

## ✅ Takeaways

- Configurable pipelines with multi-team ownership
- Weighted scoring and trend analytics
- One place to see Build → Test → Deploy status
- Ready to extend for production needs

---

## 🧠 Thought process

- Start with the domain: Organization → Team → Project → Pipeline → Stage → SubStage → Run
- JSON-first design so teams can self-serve pipeline definitions without code changes
- Pure service for scoring (deterministic, testable), signals for quick result scaffolding
- Normalize weights at read-time to be resilient to imperfect configs
- Keep APIs minimal but composable; add GUI pages for a demo-friendly story

---

## ⚖️ Risks and rewards

### Risks
- Naming drift in `owner_team` across JSON files can cause duplicate/ambiguous teams
- Misconfigured weights or missing validation may skew overall scores
- Signals can hide side-effects at scale; prefer explicit services or domain events later
- No RBAC yet — cross-team updates are possible if not controlled

### Rewards
- Single, unified view of Build → Test → Deploy across teams and projects
- Fast onboarding: drop a JSON, load, simulate, and visualize
- Comparable, normalized metrics over time and across pipelines
- Clear path to productionization (Celery, RBAC, Grafana, tests)

---

## ⏭️ If I had more time

- RBAC and auth flows scoped to `owner_team`; audit logs for updates
- Celery workers to execute auto DoD checks with retries/backoff; webhook ingestion
- JSON schema or Pydantic validation with rich error reporting in the loader
- OpenAPI/Swagger docs; Postman collection for interviews and demos
- Unit and integration tests for loader, scoring, signals, and key API endpoints
- Caching and pagination in trend endpoints; performance profiling
- React dashboard with filters (team/date/status), and mini trend sparklines per stage
- Observability: structured logging, tracing, metrics; health checks