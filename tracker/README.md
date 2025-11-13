# Tracker Django App

This directory contains a Django app `tracker` which implements an Automation Build & Test Tracker.

Quick notes:

- Add `tracker` to your project's `INSTALLED_APPS` in `settings.py`.
- Place pipeline JSON files under `configs/` and load them with:

```bash
python manage.py load_pipeline_config configs/pipeline_FW.json
```

- To create a simulated run for pipeline id 1:

```bash
python manage.py simulate_run 1
```

APIs are mounted under `api/` via the router in `tracker.urls`:

- `POST /api/runs/` - create a run (provide `pipeline_id` in JSON)
- `POST /api/runs/{id}/update_stage/` - update a stage or substage result
- `GET /api/runs/{id}/summary/` - hierarchical breakdown
- `GET /api/pipelines/{id}/trend/?n=10` - last N run scores

Weighting notes:
- Stage weights and SubStage weights are normalized when computing a run's overall score.
