# WorkForce AI Pro — HR Attrition Prediction & Workforce Intelligence Platform

A full-stack workforce management platform with an AI-driven attrition prediction engine.

## What's included in this build

### Backend (`/backend`) — FastAPI + MySQL + SQLAlchemy
- JWT authentication (access + refresh tokens), bcrypt password hashing
- Role-based access control: **Admin, HR, Manager, Employee**
- Modules: Employees, Departments, Attendance, Leave, Payroll, Notifications,
  Chat messages, Documents, Audit Logs (models ready)
- **AI Attrition Prediction Engine** (`app/ml/`):
  - `train.py` — trains a scikit-learn pipeline (RandomForest / GradientBoosting /
    LogisticRegression) with preprocessing (scaling + one-hot encoding)
  - `predict.py` — loads the active model and scores employees, with basic
    feature-importance explanations
  - Endpoints for single & batch prediction, a risk-monitoring feed, an
    attrition analytics summary, and HR intervention tracking
- Dashboard/analytics endpoints (headcount, attendance trend, leave stats)
- Verified end-to-end: trained on a synthetic 800-row dataset (80% accuracy)
  and confirmed correct risk classification on a test profile

### Frontend (`/frontend`) — React (Vite) + Tailwind CSS v4 + Recharts
- Login page + JWT-aware Axios client with auto token refresh
- Role-aware sidebar navigation and route protection
- Pages: Dashboard (charts), Employees (search/list), Attrition Risk Monitor
  (risk distribution pie chart + at-risk employee table + "run predictions"
  action), Leave (with approve/reject), Attendance, Payroll
- Build verified clean (`npm run build` succeeds)

## What's NOT yet built (roadmap)
- Employee create/edit forms (list + detail views exist; forms are next)
- Chat/messaging UI, document upload UI
- Reports & export (PDF/Excel), audit log viewer
- Workflow/task management, performance review module
- Workforce forecasting (time-series), AI recommendation engine
- Alembic migrations (currently uses `create_all` — fine for dev, not for prod)
- Automated test suite
- Docker Compose for one-command local spin-up

## Getting started

### 1. Backend

```bash
cd backend
python -m venv venv && source : venv\Scripts\activate 
pip install -r requirements.txt

# Create a MySQL database first:
#   CREATE DATABASE workforce_ai_pro;
# Then set connection details via environment variables or a .env file:
#   DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SECRET_KEY

uvicorn app.main:app --reload --port 8000
```

On first run, tables are created automatically. Seed demo data (departments,
an admin user, and 5 sample employees):

```bash
python -m app.seed
```

Admin login: `admin@workforceai.com` / `Admin@123`

API docs: http://localhost:8000/docs

### 2. Train the AI attrition model

A synthetic sample dataset is included for a quick demo:

```bash
cd backend
python -m app.ml.train --csv sample_attrition_data.csv --algorithm random_forest
```

This writes a versioned model to `app/ml/artifacts/` and marks it active.
For production, export real employee data in the same column schema
(see `NUMERIC_FEATURES` / `CATEGORICAL_FEATURES` in `app/ml/train.py`) and
retrain periodically.

Once trained, use `/api/v1/ai/predict/batch/all` (or the "Run Predictions"
button on the Attrition page) to score all active employees.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:5173 and proxies `/api` calls to the backend on
port 8000 (see `vite.config.js`).

## Architecture notes
- Auth: stateless JWT, 8-hour access tokens, 7-day refresh tokens
- RBAC is enforced at the API layer via FastAPI dependencies
  (`require_roles(...)`), not just hidden in the UI
- The AI model is decoupled from the API — it's a versioned artifact loaded
  at inference time, so retraining doesn't require redeploying the backend
- `Employee` rows carry the same fields the ML pipeline expects, so no ETL
  step is needed between HR data and the prediction engine
