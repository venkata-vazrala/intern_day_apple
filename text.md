Perfect — you’re thinking like a system architect now.
You already have the conceptual and data model; now you want to **drive Copilot** to scaffold your Django app — and you want it to understand everything upfront (stages, substages, JSON-configurable setup, and backend logic).

Below is a **ready-to-paste Copilot master prompt** you can drop right into VS Code or GitHub Copilot Chat.
It gives Copilot a **complete set of detailed instructions, goals, structure, and coding expectations**, so it will generate coherent, modular, and configurable code for your **Automation Build & Test Tracker**.

---

## 🧠 **Copilot Master Prompt for Automation Build & Test Tracker**

> Paste this entire block into Copilot Chat (or in a new comment in your main file) before starting generation.

---

````text
### PROJECT CONTEXT

You are building a Django-based **Automation Build and Test Tracker** for a multi-team environment.

The system should track and measure the Build → Test → Deploy lifecycle for multiple projects and teams.
Each project can define its own stages and sub-stages through a **configurable JSON file**, which defines:
- Stages and sub-stages names
- Their weightages
- Their "Definition of Done" (manual or automated)
- Their validation endpoints if automated

The tracker should compute:
- Weighted progress per stage and sub-stage
- Overall score per run
- Trend of scores over time
- Manual confirmation and automated validation for “Definition of Done”
- Aggregation and visualization-ready APIs

The backend must be cleanly structured using Django + Django REST Framework (DRF).

---

### REQUIREMENTS SUMMARY

#### Core Entities:
1. **Organization**
2. **Team**
3. **Project**
4. **Pipeline**
5. **Stage**
6. **SubStage**
7. **Run (Execution)**
8. **StageResult**
9. **SubStageResult**

#### Relationships:
- Organization → Team → Project → Pipeline
- Pipeline → Stage → SubStage
- Run → StageResult → SubStageResult

Each stage/sub-stage belongs to one pipeline, with weight and order attributes.
Each run contains the results (status, start/end, completion %, etc.).
Overall completion % = Weighted sum of completed stages.

---

### CONFIGURATION SYSTEM (JSON-BASED)

Create a `configs/` folder inside the Django project root.
Each pipeline can be initialized or updated from a JSON file placed there.

Example JSON structure (`configs/pipeline_FW.json`):

```json
{
  "pipeline_name": "FW Build Pipeline",
  "description": "Build → Test → Deploy lifecycle for system firmware",
  "stages": [
    {
      "name": "Build",
      "weight": 0.4,
      "substages": [
        {"name": "Source Sync", "weight": 0.2, "definition_of_done": "Repo synced successfully", "type": "auto", "endpoint": "/api/checks/source_sync/"},
        {"name": "Compilation", "weight": 0.4, "definition_of_done": "Build completes without errors", "type": "auto", "endpoint": "/api/checks/build/"},
        {"name": "Binary Signing", "weight": 0.4, "definition_of_done": "Image signed successfully", "type": "manual"}
      ]
    },
    {
      "name": "Test",
      "weight": 0.4,
      "substages": [
        {"name": "Unit Tests", "weight": 0.3, "definition_of_done": "All tests passed", "type": "auto", "endpoint": "/api/checks/unit_tests/"},
        {"name": "Integration Tests", "weight": 0.7, "definition_of_done": "All integrations verified", "type": "manual"}
      ]
    },
    {
      "name": "Deploy",
      "weight": 0.2,
      "substages": [
        {"name": "Artifact Upload", "weight": 0.5, "definition_of_done": "Uploaded to server", "type": "auto", "endpoint": "/api/checks/upload/"},
        {"name": "Tag Release", "weight": 0.5, "definition_of_done": "Release tagged successfully", "type": "manual"}
      ]
    }
  ]
}
````

A management command should load this JSON and populate/update the pipeline structure in the database.
Command example:

```bash
python manage.py load_pipeline_config configs/pipeline_FW.json
```

This command should:

* Create pipeline if missing.
* Create/update stages and substages with corresponding weights and DoD data.
* Preserve ordering and relationships.

---

### MODEL DESIGN GUIDELINES

Create models in `tracker/models.py`:

* **Stage** and **SubStage** models must include fields:

  * `weight` (FloatField)
  * `order` (IntegerField)
  * `definition_of_done` (TextField)
  * `auto_check_endpoint` (CharField, optional)
  * `dod_type` (CharField: manual/auto)

* **Run**, **StageResult**, and **SubStageResult** must store:

  * start_time, end_time, status, completion %, and references to related entities.

* **Run.overall_score** should be computed dynamically using the weights.

* Create a service file (`tracker/services.py`) with a helper:

  ```python
  def calculate_run_score(run_id: int) -> float:
      # Weighted score calculation logic
  ```

---

### API AND SERIALIZERS

Use Django REST Framework.

Endpoints required:

* `POST /api/runs/` → Create new run.
* `POST /api/runs/{id}/update_stage/` → Update stage/substage status.
* `GET /api/runs/{id}/summary/` → Full hierarchical breakdown of results.
* `GET /api/pipelines/{id}/trend/` → Show trend metrics for last N runs.

Serializers:

* `RunSerializer`
* `StageResultSerializer`
* `SubStageResultSerializer`
* `PipelineSerializer`

Views:

* Implement `RunViewSet` with custom actions: `summary`, `trend`.
* On sub-stage update, trigger recalculation of overall score.

---

### MANAGEMENT COMMANDS

1. `load_pipeline_config`
   Load/update pipeline structure from JSON file.

2. `simulate_run` (optional)
   Populate a fake run for testing to visualize data flow.

---

### ADDITIONAL NOTES

* Store all configuration JSON files under `configs/` folder.
* Allow JSON reload at any time to update pipeline definitions.
* Make sure weights always normalize correctly (sum up to 1.0 or 100%).
* Ensure cascading deletion: deleting a pipeline removes all child stages/substages.
* Use signals to automatically create StageResults/SubStageResults when a new run is created.
* Use Django Admin for quick configuration browsing.
* Add meaningful `__str__` methods for all models.
* Add a `README.md` auto-generated template summarizing setup.

---

### FILES TO GENERATE

Copilot, generate and fill in the following:

```
tracker/
  __init__.py
  models.py
  serializers.py
  views.py
  urls.py
  services.py
  admin.py
  management/
    commands/
      load_pipeline_config.py
      simulate_run.py
  signals.py
```

Then create a `settings.py` addition to include `tracker` in `INSTALLED_APPS`.

---

### CODING STYLE GUIDELINES

* Follow PEP8.
* Use Django ORM relations, avoid raw SQL.
* Use docstrings on each class and function.
* Ensure reusability and clear separation of layers (models, services, views).
* Add inline comments for weight computation logic.
* Prefer type hints where possible.
* Avoid hardcoded stage names (use JSON-defined structure).
* For testing, generate 3 dummy pipelines from 3 JSON configs.

---

### GOAL

Generate a **fully functional Django REST API** for a **multi-team Automation Build and Test Tracker**,
where **stages and sub-stages are dynamically configurable from JSON**,
and **each run computes weighted progress and trends over time**.

---

### AFTER SETUP

Once Copilot finishes generating, I’ll:

* Run `python manage.py makemigrations && migrate`
* Load a sample JSON config
* Create test runs via API
* View dashboard-ready data in `/api/runs/{id}/summary/`

---

````

---

## 💡 Tips for using this with Copilot effectively

1. **Start from your Django project root**, and paste this in a new file (like `tracker/README_FOR_COPILOT.md`) or directly into Copilot Chat.
2. Then, **ask Copilot file by file**:
   - “Generate `tracker/models.py` as per the above requirements.”
   - “Now create the `load_pipeline_config` command to load pipeline JSON into the DB.”
   - “Generate `services.py` with `calculate_run_score(run_id)` implementation.”
   - “Generate DRF serializers and views for runs and stage results.”
3. If Copilot misses relationships or names, gently nudge it — “Ensure `Stage` has a FK to `Pipeline` and `SubStage` has FK to `Stage`.”
4. Once your models are done, run:
   ```bash
   python manage.py makemigrations tracker
   python manage.py migrate
````

5. Test the JSON configuration loader:

   ```bash
   python manage.py load_pipeline_config configs/pipeline_FW.json
   ```
6. You can later extend Copilot’s context to generate your **frontend (dashboard UI)** in React or Django templates, once the APIs are stable.

---

Would you like me to include an **example JSON → database seeding logic** snippet (the part that parses and creates pipelines/stages/substages) so you can show Copilot exactly what logic to follow in the management command?
