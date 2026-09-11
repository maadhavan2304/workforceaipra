import json
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.employee import Employee, Department
from app.models.attrition import AttritionPrediction, HRIntervention
from app.models.hr_ops import Notification
from app.models.user import User
from app.ml import predict as ml_predict

router = APIRouter(prefix="/api/v1/ai", tags=["AI Attrition Intelligence"])


def _employee_to_features(emp: Employee, db: Session) -> dict:
    dept = db.query(Department).filter(Department.id == emp.department_id).first()
    return {
        "age": emp.age,
        "monthly_income": emp.monthly_income,
        "years_at_company": emp.years_at_company,
        "years_in_current_role": emp.years_in_current_role,
        "job_satisfaction": emp.job_satisfaction,
        "work_life_balance": emp.work_life_balance,
        "performance_rating": emp.performance_rating,
        "distance_from_home": emp.distance_from_home,
        "num_companies_worked": emp.num_companies_worked,
        "total_working_years": emp.total_working_years,
        "gender": emp.gender,
        "overtime": emp.overtime,
        "department": dept.name if dept else None,
    }


@router.post("/predict/{employee_id}")
def predict_single(
    employee_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR", "Manager")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    try:
        features = _employee_to_features(emp, db)
        result = ml_predict.predict_employee(features)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    record = AttritionPrediction(
        employee_id=emp.id,
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        top_factors=json.dumps(result["top_factors"]),
        model_version=result["model_version"],
    )
    db.add(record)

    # Auto-alert for high risk employees
    if result["risk_level"] in ("High", "Critical") and emp.user:
        db.add(Notification(
            user_id=emp.user.id,
            title="Attrition Risk Alert",
            message=f"Your engagement signals indicate a {result['risk_level'].lower()} attrition risk. HR will reach out.",
            category="attrition_alert",
        ))

    db.commit()
    db.refresh(record)
    return {
        "employee_id": emp.id,
        "employee_name": emp.full_name,
        **result,
    }


@router.post("/predict/batch/all")
def predict_batch_all(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR")),
):
    employees = db.query(Employee).filter(Employee.status == "Active").all()
    if not employees:
        return {"predicted": 0, "results": []}

    rows = [_employee_to_features(e, db) for e in employees]
    df = pd.DataFrame(rows)

    try:
        preds = ml_predict.predict_batch(df)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    results = []
    for emp, pred in zip(employees, preds):
        record = AttritionPrediction(
            employee_id=emp.id,
            risk_score=pred["risk_score"],
            risk_level=pred["risk_level"],
            model_version=pred["model_version"],
        )
        db.add(record)
        results.append({"employee_id": emp.id, "employee_name": emp.full_name, **pred})

    db.commit()
    return {"predicted": len(results), "results": results}


@router.get("/risk-monitor")
def risk_monitor(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR", "Manager")),
    risk_level: Optional[str] = None,
    limit: int = 200,
):
    """Latest prediction per employee, for the risk monitoring dashboard."""
    subq = (
        db.query(
            AttritionPrediction.employee_id,
            AttritionPrediction.risk_score,
            AttritionPrediction.risk_level,
            AttritionPrediction.predicted_at,
        )
        .order_by(AttritionPrediction.employee_id, AttritionPrediction.predicted_at.desc())
        .all()
    )
    latest_by_employee = {}
    for row in subq:
        if row.employee_id not in latest_by_employee:
            latest_by_employee[row.employee_id] = row

    results = []
    for emp_id, row in latest_by_employee.items():
        if risk_level and row.risk_level != risk_level:
            continue
        emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if not emp:
            continue
        results.append({
            "employee_id": emp_id,
            "employee_name": emp.full_name,
            "department_id": emp.department_id,
            "risk_score": row.risk_score,
            "risk_level": row.risk_level,
            "predicted_at": row.predicted_at,
        })

    results.sort(key=lambda r: r["risk_score"], reverse=True)
    return results[:limit]


@router.get("/analytics/summary")
def attrition_analytics_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR", "Manager")),
):
    total_active = db.query(Employee).filter(Employee.status == "Active").count()
    total_exited = db.query(Employee).filter(Employee.status.in_(["Resigned", "Terminated"])).count()

    latest = risk_monitor(db=db, _=_, risk_level=None, limit=10000)
    level_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for r in latest:
        level_counts[r["risk_level"]] = level_counts.get(r["risk_level"], 0) + 1

    total_workforce = total_active + total_exited
    attrition_rate = round((total_exited / total_workforce) * 100, 2) if total_workforce else 0.0

    return {
        "total_active_employees": total_active,
        "total_exited_employees": total_exited,
        "attrition_rate_percent": attrition_rate,
        "risk_distribution": level_counts,
        "high_risk_employee_count": level_counts["High"] + level_counts["Critical"],
    }


# ---------- HR Interventions (Decision Support) ----------
@router.post("/interventions")
def create_intervention(
    employee_id: int, action_type: str, notes: Optional[str] = None,
    prediction_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "HR", "Manager")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    intervention = HRIntervention(
        employee_id=employee_id,
        prediction_id=prediction_id,
        action_type=action_type,
        notes=notes,
        created_by=current_user.id,
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


@router.get("/interventions")
def list_interventions(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR", "Manager")),
    employee_id: Optional[int] = None,
):
    q = db.query(HRIntervention)
    if employee_id:
        q = q.filter(HRIntervention.employee_id == employee_id)
    return q.order_by(HRIntervention.created_at.desc()).all()
