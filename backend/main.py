from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

# Dodaj current directory do path
sys.path.append(str(Path(__file__).parent))

from config import settings
from database import init_db
from routes import files, data

# Inicjalizacja bazy danych
init_db()

# Tworzenie aplikacji FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API dla aplikacji do zarządzania danymi SWD"
)

# CORS - dla developmentu i desktopa
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],  # W produkcji ogranicz!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rejestracja routerów
app.include_router(files.router)
app.include_router(data.router)

# Health check endpoint
@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Serwowanie statycznych plików React (dla desktopa)
# W developmencie React działa na porcie 3000
# W produkcji (desktop) React build jest serwowany stąd
frontend_build = Path(__file__).parent.parent / "frontend" / "build"
if frontend_build.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Upload directory: {settings.UPLOAD_DIR}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )