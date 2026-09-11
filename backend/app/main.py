from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import auth, employees, hr_ops, attrition, dashboard

# Import models package so all tables register on Base.metadata before create_all
import app.models  # noqa: F401

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack workforce management & AI-driven attrition prediction platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # For production use Alembic migrations instead of create_all
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(hr_ops.router)
app.include_router(attrition.router)
app.include_router(dashboard.router)


@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
