from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: str = "Present"
    shift: Optional[str] = None


class AttendanceOut(AttendanceCreate):
    id: int
    hours_worked: Optional[float] = None

    class Config:
        from_attributes = True


class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None


class LeaveDecision(BaseModel):
    status: str  # Approved / Rejected
    approved_by: Optional[int] = None


class LeaveOut(LeaveCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class PayrollCreate(BaseModel):
    employee_id: int
    month: int
    year: int
    basic_salary: float
    allowances: float = 0
    deductions: float = 0


class PayrollOut(PayrollCreate):
    id: int
    net_salary: float
    status: str

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    category: str
    is_read: int
    created_at: datetime

    class Config:
        from_attributes = True
