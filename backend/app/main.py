from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import get_password_hash
from app.models.models import Usuario

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.on_event("startup")
def create_default_admin():
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        existing = session.query(Usuario).filter(Usuario.username == "admin").first()
        if not existing:
            admin = Usuario(
                username="admin",
                email="admin@diligencia.pa",
                full_name="Administrador",
                rol="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            session.add(admin)
            session.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)