from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Obsługa obu wersji SQLAlchemy (1.x i 2.x)
try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    
from config import settings

# Silnik bazy danych
# Desktop: SQLite (check_same_thread=False dla FastAPI)
# Web: Zmień na PostgreSQL engine bez check_same_thread
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class dla modeli
Base = declarative_base()

# Dependency dla FastAPI
def get_db():
    """Dependency do pobierania sesji bazy danych"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicjalizacja bazy danych - tworzy wszystkie tabele"""
    Base.metadata.create_all(bind=engine)