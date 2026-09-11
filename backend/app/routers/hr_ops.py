from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.hr_ops import Attendance, LeaveRequest, Payroll, Notification
from app.models.user import User
from app.schemas.hr_ops import (
    AttendanceCreate, AttendanceOut, LeaveCreate, LeaveOut, LeaveDecision,
    PayrollCreate, PayrollOut, NotificationOut,
)

router = APIRouter(prefix="/api/v1", tags=["Attendance, Leave & Payroll"])


# ---------- Attendance ----------
@router.post("/attendance", response_model=AttendanceOut, status_code=201)
def mark_attendance(payload: AttendanceCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    record = Attendance(**payload.model_dump())
    if record.check_in and record.check_out:
        delta = (
            (record.check_out.hour * 60 + record.check_out.minute)
            - (record.check_in.hour * 60 + record.check_in.minute)
        )
        record.hours_worked = round(delta / 60, 2)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/attendance", response_model=List[AttendanceOut])
def list_attendance(
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
    employee_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    q = db.query(Attendance)
    if employee_id:
        q = q.filter(Attendance.employee_id == employee_id)
    if date_from:
        q = q.filter(Attendance.date >= date_from)
    if date_to:
        q = q.filter(Attendance.date <= date_to)
    return q.order_by(Attendance.date.desc()).all()


# ---------- Leave ----------
@router.post("/leaves", response_model=LeaveOut, status_code=201)
def request_leave(payload: LeaveCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    leave = LeaveRequest(**payload.model_dump())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


@router.get("/leaves", response_model=List[LeaveOut])
def list_leaves(
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
    employee_id: Optional[int] = None, status: Optional[str] = None,
):
    q = db.query(LeaveRequest)
    if employee_id:
        q = q.filter(LeaveRequest.employee_id == employee_id)
    if status:
        q = q.filter(LeaveRequest.status == status)
    return q.order_by(LeaveRequest.created_at.desc()).all()


@router.patch("/leaves/{leave_id}/decision", response_model=LeaveOut)
def decide_leave(
    leave_id: int, payload: LeaveDecision, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "HR", "Manager")),
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    leave.status = payload.status
    leave.approved_by = payload.approved_by or current_user.id
    db.commit()
    db.refresh(leave)
    return leave


# ---------- Payroll ----------
@router.post("/payroll", response_model=PayrollOut, status_code=201)
def generate_payroll(
    payload: PayrollCreate, db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR")),
):
    net = payload.basic_salary + payload.allowances - payload.deductions
    record = Payroll(**payload.model_dump(), net_salary=net)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/payroll", response_model=List[PayrollOut])
def list_payroll(
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
    employee_id: Optional[int] = None, year: Optional[int] = None, month: Optional[int] = None,
):
    q = db.query(Payroll)
    if employee_id:
        q = q.filter(Payroll.employee_id == employee_id)
    if year:
        q = q.filter(Payroll.year == year)
    if month:
        q = q.filter(Payroll.month == month)
    return q.all()


# ---------- Notifications ----------
@router.get("/notifications", response_model=List[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    note = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")
    note.is_read = 1
    db.commit()
    db.refresh(note)
    return note
