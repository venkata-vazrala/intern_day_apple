---
title: Automation Build & Test Tracker
theme: default
paginate: true
marp: true
---

# 🧩 Automation Build & Test Tracker
*A scalable Django-based system for multi-team build and validation tracking*  

**Author:** Venkata Gunasekhar V  
**Tools:** Django · PostgreSQL · Celery · Jenkins · Docker  

---

## 🎯 Motivation & Goals

### Problem
- Multiple teams with distinct build/test flows  
- Manual DoD checks and scattered Jenkins jobs  
- No unified visibility or weighted tracking  

### Goal
- Centralized, configurable tracker for automation pipelines  
- Weighted scoring & trend tracking  
- Unified dashboard for cross-team insights  

---

## 🏗️ High-Level Architecture

**Components:**
- Django + DRF → REST backend, APIs  
- PostgreSQL → Core datastore  
- Celery + Redis → Asynchronous jobs  
- Jenkins → Build & test triggers  
- Docker → Execution isolation  

**Supports:**
- Webhook & polling-based updates  
- Grafana/Plotly-ready metrics  

---

## 🧱 Core Domain Model

**Entities**
- Organization / Team / Project  
- Pipeline (Build → Test → Deploy)  
- Stage / SubStage (Configurable via JSON)  
- Definition of Done (Manual or Automated)  
- Run / StageResult / SubStageResult  

**Key Idea:**  
Configurable JSON-driven structure with weighted scoring.

---

## 🔄 Data Flow Overview

1. **Trigger:** Jenkins job or webhook → creates a Run  
2. **Processing:** Django saves stage/substage results  
3. **Computation:** Weighted completion scores  
4. **Trend Aggregation:** Celery tasks  
5. **Visualization:** Dashboard or REST API summary  

---

## 📊 Scoring Logic

### Stage Completion
