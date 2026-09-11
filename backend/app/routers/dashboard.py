from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.employee import Employee, Department
from app.models.hr_ops import Attendance, LeaveRequest
from app.models.user import User

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total_employees = db.query(Employee).filter(Employee.status == "Active").count()
    total_departments = db.query(Department).count()

    today = date.today()
    present_today = (
        db.query(Attendance)
        .filter(Attendance.date == today, Attendance.status == "Present")
        .count()
    )
    on_leave_today = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.status == "Approved",
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
        )
        .count()
    )
    pending_leave_requests = db.query(LeaveRequest).filter(LeaveRequest.status == "Pending").count()

    dept_breakdown = (
        db.query(Department.name, func.count(Employee.id))
        .join(Employee, Employee.department_id == Department.id)
        .filter(Employee.status == "Active")
        .group_by(Department.name)
        .all()
    )

    return {
        "total_active_employees": total_employees,
        "total_departments": total_departments,
        "present_today": present_today,
        "on_leave_today": on_leave_today,
        "pending_leave_requests": pending_leave_requests,
        "department_breakdown": [{"department": d[0], "count": d[1]} for d in dept_breakdown],
    }


@router.get("/attendance-trend")
def attendance_trend(db: Session = Depends(get_db), _: User = Depends(get_current_user), days: int = 14):
    start = date.today() - timedelta(days=days)
    rows = (
        db.query(Attendance.date, func.count(Attendance.id))
        .filter(Attendance.date >= start, Attendance.status == "Present")
        .group_by(Attendance.date)
        .order_by(Attendance.date)
        .all()
    )
    return [{"date": str(r[0]), "present_count": r[1]} for r in rows]
