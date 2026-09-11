from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    designation = Column(String(150), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    date_of_joining = Column(Date, nullable=True)
    date_of_exit = Column(Date, nullable=True)
    status = Column(String(30), default="Active")  # Active, Resigned, Terminated, On Leave

    # Attrition-model relevant fields
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    monthly_income = Column(Float, nullable=True)
    years_at_company = Column(Float, nullable=True)
    years_in_current_role = Column(Float, nullable=True)
    job_satisfaction = Column(Integer, nullable=True)  # 1-4 scale
    work_life_balance = Column(Integer, nullable=True)  # 1-4 scale
    performance_rating = Column(Integer, nullable=True)  # 1-5 scale
    overtime = Column(String(5), nullable=True)  # Yes/No
    distance_from_home = Column(Float, nullable=True)
    num_companies_worked = Column(Integer, nullable=True)
    total_working_years = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    user = relationship("User", back_populates="employee", uselist=False, foreign_keys="User.employee_id")
