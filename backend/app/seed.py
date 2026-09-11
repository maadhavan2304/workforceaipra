"""
Seed script: creates departments, an admin user, and sample employees
so you can explore the platform immediately after setup.

Usage:
    python -m app.seed
"""
from datetime import date

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User, RoleEnum
from app.models.employee import Employee, Department

import app.models  # noqa: F401 - ensure all tables are registered


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already has users - skipping seed.")
            return

        depts = {}
        for name in ["Engineering", "Sales", "HR", "Finance", "Support"]:
            d = Department(name=name)
            db.add(d)
            db.flush()
            depts[name] = d

        admin = User(
            email="admin@workforceai.com",
            hashed_password=hash_password("Admin@123"),
            full_name="System Administrator",
            role=RoleEnum.ADMIN,
        )
        db.add(admin)

        sample_employees = [
            ("EMP001", "Aditi Sharma", "aditi.sharma@workforceai.com", "Engineering", "Senior Engineer", 5.2, 3, 3, "No"),
            ("EMP002", "Rahul Verma", "rahul.verma@workforceai.com", "Sales", "Sales Executive", 0.7, 2, 2, "Yes"),
            ("EMP003", "Priya Nair", "priya.nair@workforceai.com", "HR", "HR Manager", 6.1, 4, 4, "No"),
            ("EMP004", "Karthik Iyer", "karthik.iyer@workforceai.com", "Finance", "Financial Analyst", 1.3, 2, 3, "Yes"),
            ("EMP005", "Sneha Reddy", "sneha.reddy@workforceai.com", "Support", "Support Lead", 3.4, 3, 4, "No"),
        ]
        for code, name, email, dept, designation, years, sat, wlb, ot in sample_employees:
            emp = Employee(
                employee_code=code,
                full_name=name,
                email=email,
                department_id=depts[dept].id,
                designation=designation,
                date_of_joining=date(2024, 1, 1),
                status="Active",
                age=28,
                gender="Female" if name.split()[0][-1] == "i" else "Male",
                monthly_income=60000,
                years_at_company=years,
                years_in_current_role=min(years, 2),
                job_satisfaction=sat,
                work_life_balance=wlb,
                performance_rating=3,
                overtime=ot,
                distance_from_home=12,
                num_companies_worked=2,
                total_working_years=years + 2,
            )
            db.add(emp)

        db.commit()
        print("Seed complete.")
        print("Admin login -> email: admin@workforceai.com | password: Admin@123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
