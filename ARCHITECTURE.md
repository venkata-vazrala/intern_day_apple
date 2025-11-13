# System Architecture Diagram

## Entity Relationship Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                         Organization                            │
│                 (ABC COMPANY - Firmware)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ has many
                         ▼
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼────────┐
│  Team: Build   │              │  Team: Test      │
│   Automation   │              │  Validation      │
└───────┬────────┘              └─────────┬────────┘
        │                                  │
        │ has many                         │ has many
        ▼                                  ▼
┌───────────────┐                ┌──────────────────┐
│ Project:      │                │ Project:         │
│ FW-MCU_VM  │                │ FW-MPU      │
└───────┬───────┘                └──────────┬───────┘
        │                                   │
        │ has many                          │ has many
        ▼                                   ▼
┌────────────────────────────────────────────────────┐
│              Pipeline (JSON-configured)            │
│          "FW Build Pipeline v1.0"               │
└────────────────┬───────────────────────────────────┘
                 │
                 │ has many (ordered)
                 ▼
    ┌────────────┴─────────────┬──────────────┐
    │                          │              │
┌───▼──────────┐     ┌─────────▼────┐   ┌────▼──────┐
│ Stage: Build │     │ Stage: Test  │   │Stage:     │
│ weight: 0.4  │     │ weight: 0.4  │   │Deploy     │
└───┬──────────┘     └─────────┬────┘   │weight: 0.2│
    │                          │         └────┬──────┘
    │ has many                 │              │
    ▼                          ▼              ▼
┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐
│SubStage:        │  │SubStage:         │  │SubStage:       │
│Source Sync      │  │Unit Tests        │  │Artifact Upload │
│weight: 0.2      │  │weight: 0.3       │  │weight: 0.5     │
│type: auto       │  │type: auto        │  │type: auto      │
└─────────────────┘  └──────────────────┘  └────────────────┘
```

## Run Execution Flow

```
                    ┌──────────────┐
                    │  Create Run  │
                    │  (via API)   │
                    └──────┬───────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  Signal: post_save(Run)  │
            │  Auto-creates:           │
            │  - StageResults          │
            │  - SubStageResults       │
            └──────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │  Run.stage_results (all pending)     │
    │  ├─ Build (0%)                       │
    │  │  ├─ Source Sync (0%)              │
    │  │  ├─ Compilation (0%)              │
    │  │  └─ Binary Signing (0%)           │
    │  ├─ Test (0%)                        │
    │  │  ├─ Unit Tests (0%)               │
    │  │  └─ Integration Tests (0%)        │
    │  └─ Deploy (0%)                      │
    │     ├─ Artifact Upload (0%)          │
    │     └─ Tag Release (0%)              │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │  POST /api/runs/{id}/update_stage/  │
    │  {"substage_id": 1,                  │
    │   "completion_percent": 100}         │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │  Update SubStageResult               │
    │  Recalculate overall_score           │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │  Run.overall_score = Σ(stage.weight  │
    │  × stage_completion / total_weight)  │
    │  = 0.4×(33%) + 0.4×(0%) + 0.2×(0%)   │
    │  = 0.13 → 13%                        │
    └──────────────────────────────────────┘
```

## API Data Flow

```
Client Request                    Django Backend
─────────────                    ──────────────

GET /api/pipelines/1/
         │
         └─────────────────────────────────────►  PipelineViewSet
                                                        │
                                                        ▼
                                                   PipelineSerializer
                                                   (nested stages,
                                                    substages)
                                                        │
                    JSON Response ◄─────────────────────┘
{
  "id": 1,
  "name": "FW Build Pipeline",
  "stages": [
    {
      "name": "Build",
      "weight": 0.4,
      "substages": [...]
    }
  ]
}


POST /api/runs/
Body: {"pipeline": 1}
         │
         └─────────────────────────────────────►  RunViewSet.create()
                                                        │
                                                        ▼
                                                   Run.objects.create()
                                                        │
                                                        ▼
                                                   Signal: post_save
                                                   (auto-create results)
                                                        │
                    Run Created ◄───────────────────────┘
{
  "id": 2,
  "pipeline": 1,
  "status": "running",
  "overall_score": 0.0,
  "stage_results": [...]
}


GET /api/pipelines/1/trend/?n=5
         │
         └─────────────────────────────────────►  PipelineViewSet.trend()
                                                        │
                                                        ▼
                                                   Run.objects
                                                   .filter(pipeline=1)
                                                   .order_by('-start_time')
                                                   [:5]
                                                        │
                    Trend Data  ◄───────────────────────┘
[
  {"run_id": 5, "overall_score": 100.0},
  {"run_id": 4, "overall_score": 58.33},
  {"run_id": 3, "overall_score": 81.67}
]
```

## Score Calculation Example

```
Pipeline: FW Build Pipeline
─────────────────────────────────────────────────────────────

Stage: Build (weight: 0.4)
├─ Source Sync (100%)      ┐
├─ Compilation (100%)      │─► Average = 100% → Build = 100%
└─ Binary Signing (100%)   ┘

Stage: Test (weight: 0.4)
├─ Unit Tests (100%)       ┐
└─ Integration Tests (50%) ┘─► Average = 75% → Test = 75%

Stage: Deploy (weight: 0.2)
├─ Artifact Upload (0%)    ┐
└─ Tag Release (0%)        ┘─► Average = 0% → Deploy = 0%

Overall Score Calculation:
───────────────────────────
= (Build_weight × Build_completion) +
  (Test_weight × Test_completion) +
  (Deploy_weight × Deploy_completion)

= (0.4 × 100%) + (0.4 × 75%) + (0.2 × 0%)
= 40% + 30% + 0%
= 70%

Normalized by total stage weight (1.0):
70% / 1.0 = 70% ✓
```

## Multi-Team Collaboration Model

```
        ┌──────────────────────────────────┐
        │   Pipeline: FW Nightly        │
        │   (Shared across 3 teams)        │
        └───────────┬──────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌───────────┐ ┌──────────┐ ┌──────────┐
│Team: Build│ │Team: Test│ │Team:     │
│           │ │          │ │Deploy    │
│Owns:      │ │Owns:     │ │Owns:     │
│Build      │ │Test      │ │Deploy    │
│stage      │ │stage     │ │stage     │
└───────────┘ └──────────┘ └──────────┘
     │             │             │
     ▼             ▼             ▼
  Updates      Updates      Updates
  substages    substages    substages
  via API      via API      via API
     │             │             │
     └──────┬──────┴──────┬──────┘
            │             │
            ▼             ▼
    Overall Run Score Aggregated
         (70% complete)
```

## Technology Stack

```
┌────────────────────────────────────────┐
│         Frontend (Future)              │
│  React/Vue + Chart.js + Axios          │
└────────────┬───────────────────────────┘
             │ HTTP/REST
             ▼
┌────────────────────────────────────────┐
│         Django REST Framework          │
│  ├─ ViewSets (Pipelines, Runs)        │
│  ├─ Serializers (nested)               │
│  └─ Router (URL routing)               │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│         Django ORM / Models            │
│  ├─ Organization, Team, Project        │
│  ├─ Pipeline, Stage, SubStage          │
│  └─ Run, StageResult, SubStageResult   │
└────────────┬───────────────────────────┘
             │
             ▼
┌────────────────────────────────────────┐
│         SQLite Database                │
│  (Production: PostgreSQL)              │
└────────────────────────────────────────┘

External Systems (Future Integration):
├─ Jenkins (webhook → create runs)
├─ GitHub Actions (status updates)
└─ Slack (notifications)
```

## Deployment Architecture (Future)

```
Internet
   │
   ▼
┌─────────────┐
│   Nginx     │  ← Reverse proxy + static files
│  (Port 80)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Gunicorn   │  ← WSGI server
│  (8 workers)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Django    │  ← Application
│   + DRF     │
└──────┬──────┘
       │
   ┌───┴────┐
   ▼        ▼
┌──────┐ ┌──────┐
│Postgr│ │Redis │  ← Database + Cache
│e SQL │ │      │
└──────┘ └──────┘
```

---

## Key Design Decisions

1. **JSON-driven config**: Allows teams to iterate without code changes
2. **Weighted scoring**: Reflects real importance of different stages
3. **Signal-based automation**: Reduces boilerplate, ensures consistency
4. **Nested serializers**: Clean API responses with full context
5. **Management commands**: Easy testing and data seeding
6. **Separation of concerns**: Models/Services/Serializers/Views clearly divided

This architecture scales from 1 pipeline to 1000+ pipelines across multiple organizations.
