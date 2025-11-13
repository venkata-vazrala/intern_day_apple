# Automation Build & Test Tracker

A Django + DRF backend to track multi-team Build → Test → Deploy pipelines with weighted scoring, trend metrics, and a simple GUI. Pipelines, stages, and substages are defined via JSON (owner teams, DoD, auto/manual checks, endpoints).

- Tech: Django, Django REST Framework, SQLite (dev) / PostgreSQL (prod)
- Optional: Celery + Redis for async jobs (future), Jenkins/GitHub Actions for triggers

## Features

- JSON-driven pipelines per Project/Team (stages, substages, weights, DoD, auto/manual)
- Weighted score per run; trend over time
- Ownership model: Organization → Team → Project → Pipeline; owner_team per Stage/SubStage
- REST API + basic GUI (list pipelines, per-pipeline dashboard)
- Management commands to load configs and simulate runs

## Hierarchy

Organization → Team → Project → Pipeline → Stage → SubStage → Run

- Stage/SubStage include: weight, order, dod_type (manual/auto), auto_check_endpoint, definition_of_done, owner_team
- Run computes overall_score (0–100) from weighted stage/substage progress

## Quickstart

1) Create and activate a venv (macOS zsh)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```bash
pip install django djangorestframework
```

3) Project settings (already included in this repo)
- `autotracker/settings.py` has `rest_framework` and `tracker` in `INSTALLED_APPS` and uses SQLite by default.

4) Migrations
```bash
python manage.py makemigrations tracker
python manage.py migrate
```

5) Load pipeline configs
```bash
# Single
python manage.py load_pipeline_config configs/pipeline_FW.json

# Load all in configs/
for f in configs/*.json; do echo "Loading $f"; python manage.py load_pipeline_config "$f"; done
```

6) (Optional) Simulate a run for pipeline id 1
```bash
python manage.py simulate_run 1
```

7) Start server and open GUI
```bash
python manage.py runserver 127.0.0.1:8000
# GUI:
#   /              -> Pipeline list
#   /pipelines/1/  -> Pipeline dashboard
```

## REST API

- POST /api/runs/ → Create run
- POST /api/runs/{id}/update_stage/ → Update a substage result
- GET  /api/runs/{id}/summary/ → Run breakdown with weighted score
- GET  /api/pipelines/{id}/trend/?n=10 → Last N run scores
- GET  /api/pipelines/{id}/ → Pipeline detail (stages, owner_team)

Examples
```bash
# Create a run
curl -X POST http://127.0.0.1:8000/api/runs/ \
  -H "Content-Type: application/json" \
  -d '{"pipeline_id": 1, "name": "Nightly-2025-11-12"}'

# Update a substage (team-owned)
curl -X POST http://127.0.0.1:8000/api/runs/1/update_stage/ \
  -H "Content-Type: application/json" \
  -d '{"substage_id": 3, "completion_percentage": 100, "status": "completed", "auto_validated": true}'

# Read summary + trend
curl http://127.0.0.1:8000/api/runs/1/summary/
curl http://127.0.0.1:8000/api/pipelines/1/trend/?n=10
```

## JSON Configuration

- Place files under `configs/`
- Include optional ownership fields (owner_team) on stage/substage
- Example (abbrev):
```json
{
  "organization": "ABC Firmware Division",
  "project": { "team": "Build Automation", "name": "FW-MCU_VM" },
  "pipeline_name": "FW Nightly Build",
  "stages": [
    {
      "name": "Build",
      "weight": 0.4,
      "owner_team": "Build Automation",
      "substages": [
        {"name": "Source Sync", "weight": 0.2, "type":"auto", "endpoint":"/api/checks/source_sync/", "owner_team":"Build Automation"},
        {"name": "Compilation", "weight": 0.4, "type":"auto", "endpoint":"/api/checks/build/", "owner_team":"Build Automation"},
        {"name": "Binary Signing", "weight": 0.4, "type":"manual", "owner_team":"Build Automation"}
      ]
    },
    { "name": "Test", "weight": 0.4, "owner_team":"Validation", "substages": [ /* ... */ ] },
    { "name": "Deploy", "weight": 0.2, "owner_team":"Deployment", "substages": [ /* ... */ ] }
  ]
}
```

Multi-team loading
```bash
# Load multiple pipelines (various teams/projects)
for f in configs/*.json; do python manage.py load_pipeline_config "$f"; done
```

Your provided mobile example (`configs/pipeline_mobile.json`) is supported:
- Organization: Mobile Org
- Team: Mobile Team
- Project: Mobile Project
- Build owned by Build Automation; Test owned by Validation

## Scoring

- SubStage completion: 0–100
- Stage completion: weighted mean of substages (normalize if not 1.0)
- Overall score: weighted mean of stages (normalize if not 1.0)
- Results recompute when a substage updates

## GUI

- `/` shows pipelines
- `/pipelines/<id>/` shows:
  - Overall score + latest run status
  - Stages (Build/Test/Deploy) with weights, owner_team, and per-stage progress
  - Substage table with progress and status

## Management Commands

- `load_pipeline_config <path>` → create/update pipeline/tree from JSON
- `simulate_run <pipeline_id>` → create a fake run with random progress (dev/testing)

## Project Structure (key parts)

- `tracker/`
  - `models.py`, `serializers.py`, `services.py`, `views.py`, `urls.py`, `admin.py`
  - `signals.py` (auto-create results on Run creation)
  - `management/commands/load_pipeline_config.py`, `simulate_run.py`
  - `templates/tracker/*.html` (GUI)

## Roadmap

- Async auto-validation (call auto_check_endpoint) with Celery
- Auth/RBAC per team and per stage ownership
- OpenAPI docs; unit tests for loader/score/services
- Grafana/Plotly dashboards