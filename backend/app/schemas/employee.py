from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    manager_id: Optional[int] = None


class DepartmentOut(DepartmentCreate):
    id: int

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    employee_code: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    status: Optional[str] = "Active"
    age: Optional[int] = None
    gender: Optional[str] = None
    monthly_income: Optional[float] = None
    years_at_company: Optional[float] = None
    years_in_current_role: Optional[float] = None
    job_satisfaction: Optional[int] = None
    work_life_balance: Optional[int] = None
    performance_rating: Optional[int] = None
    overtime: Optional[str] = None
    distance_from_home: Optional[float] = None
    num_companies_worked: Optional[int] = None
    total_working_years: Optional[float] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    status: Optional[str] = None
    date_of_exit: Optional[date] = None
    monthly_income: Optional[float] = None
    job_satisfaction: Optional[int] = None
    work_life_balance: Optional[int] = None
    performance_rating: Optional[int] = None
    overtime: Optional[str] = None


class EmployeeOut(EmployeeBase):
    id: int
    date_of_exit: Optional[date] = None

    class Config:
        from_attributes = True
