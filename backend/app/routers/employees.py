from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.employee import Employee, Department
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate, EmployeeOut, EmployeeUpdate, DepartmentCreate, DepartmentOut,
)

router = APIRouter(prefix="/api/v1", tags=["Employees & Departments"])


# ---------- Departments ----------
@router.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(
    payload: DepartmentCreate, db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR")),
):
    dept = Department(**payload.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/departments", response_model=List[DepartmentOut])
def list_departments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Department).all()


# ---------- Employees ----------
@router.post("/employees", response_model=EmployeeOut, status_code=201)
def create_employee(
    payload: EmployeeCreate, db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR")),
):
    if db.query(Employee).filter(Employee.employee_code == payload.employee_code).first():
        raise HTTPException(status_code=400, detail="Employee code already exists")
    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.get("/employees", response_model=List[EmployeeOut])
def list_employees(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search by name, code, or email"),
    skip: int = 0,
    limit: int = 100,
):
    q = db.query(Employee)
    if department_id:
        q = q.filter(Employee.department_id == department_id)
    if status:
        q = q.filter(Employee.status == status)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (Employee.full_name.ilike(like))
            | (Employee.employee_code.ilike(like))
            | (Employee.email.ilike(like))
        )
    return q.offset(skip).limit(limit).all()


@router.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin", "HR", "Manager")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/employees/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int, db: Session = Depends(get_db),
    _: User = Depends(require_roles("Admin")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()
    return None
