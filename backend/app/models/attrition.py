from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.core.database import Base


class AttritionPrediction(Base):
    __tablename__ = "attrition_predictions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)  # 0.0 - 1.0 probability of attrition
    risk_level = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    top_factors = Column(Text, nullable=True)  # JSON string of contributing factors
    model_version = Column(String(50), default="v1")
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False)
    algorithm = Column(String(100), nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    trained_on_rows = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=True)
    is_active = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HRIntervention(Base):
    __tablename__ = "hr_interventions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("attrition_predictions.id"), nullable=True)
    action_type = Column(String(100), nullable=False)  # 1:1 Meeting, Salary Review, Role Change...
    notes = Column(Text, nullable=True)
    status = Column(String(30), default="Planned")  # Planned, In Progress, Completed
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
