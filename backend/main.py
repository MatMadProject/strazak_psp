from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from config import settings
from database import init_db
import sys
from pathlib import Path

# Inicjalizacja bazy danych
init_db()

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# CORS dla development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routerów
from routes import firefighters, data, files

# WAŻNE: Wszystkie API routes PRZED catch-all
app.include_router(firefighters.router, prefix="/api/firefighters", tags=["firefighters"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

@app.get("/api")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# Funkcja do znalezienia ścieżki zasobów (działa z PyInstaller)
def get_resource_path(relative_path):
    """Pobierz absolutną ścieżkę do zasobu - działa z PyInstaller"""
    try:
        base_path = sys._MEIPASS
        print(f"PyInstaller mode - _MEIPASS: {base_path}")
    except AttributeError:
        base_path = Path(__file__).parent.parent
        print(f"Development mode - base: {base_path}")
    
    result_path = Path(base_path) / relative_path
    print(f"Resource path for '{relative_path}': {result_path}")
    print(f"Exists: {result_path.exists()}")
    
    return result_path

# Ścieżka do React buildu
frontend_build_path = get_resource_path("frontend/build")

# Serwuj statyczne pliki React (CSS, JS) - PRZED catch-all
if frontend_build_path.exists():
    static_path = frontend_build_path / "static"
    if static_path.exists():
        print(f"Mounting static files from: {static_path}")
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    else:
        print(f"Static folder not found: {static_path}")
else:
    print(f"Frontend build not found: {frontend_build_path}")

# CATCH-ALL ROUTE - MUSI BYĆ NA SAMYM KOŃCU!
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serwuj React app dla wszystkich ścieżek (obsługa React Router)"""
    print(f"Request for: /{full_path}")
    
    # Nie przechwytuj API routes
    if full_path.startswith("api"):
        print(f" -> API route, skipping")
        return {"error": "Not found"}
    
    # Zwróć index.html
    index_path = frontend_build_path / "index.html"
    print(f" -> Serving: {index_path}")
    
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {
            "error": "Frontend not found", 
            "path": str(frontend_build_path),
            "index_exists": index_path.exists(),
            "build_exists": frontend_build_path.exists()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)