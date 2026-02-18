from fastapi import APIRouter
from config import settings
import sys

router = APIRouter()

@router.get("/environment")
async def get_environment():
    """Zwróć informacje o środowisku"""
    return {
        "is_desktop": getattr(sys, "frozen", False),
    }

@router.get("/version")
async def get_version():
    """Zwróć wersję aplikacji"""
    return {
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
        "company": settings.COMPANY,
    }

@router.get("/info")
async def get_app_info():
    """Zwróć pełne informacje o aplikacji"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "company": settings.COMPANY,
        "is_desktop": getattr(sys, "frozen", False),
        "python_version": sys.version.split()[0]
    }