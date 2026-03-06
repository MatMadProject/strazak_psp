from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from pathlib import Path

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inteligentna inicjalizacja bazy danych
    - Sprawdza dostępność ścieżki (ważne dla baz sieciowych)
    - Tworzy bazę jeśli nie istnieje
    - Uruchamia migracje jeśli istnieje
    """
    from models import SWDRecord, ImportedFile, Firefighter, HazardousDegree  # Importuj wszystkie modele
    
    db_path = settings.DATABASE_PATH
    
    print("[DB] ═══════════════════════════════════════")
    print(f"[DB] Database path: {db_path}")
    print(f"[DB] Database type: {settings.DATABASE_TYPE}")
    
    # Sprawdź dostępność ścieżki
    if not _is_path_accessible(db_path.parent):
        error_msg = f"Baza danych jest niedostępna: {db_path}"
        if settings.DATABASE_TYPE == 'network':
            error_msg += "\n\nSprawdź czy zasób sieciowy jest dostępny i czy masz uprawnienia."
        else:
            error_msg += "\n\nSprawdź uprawnienia do folderu."
        
        print(f"[DB] {error_msg}")
        raise RuntimeError(error_msg)
    
    # SCENARIUSZ 1: Baza nie istnieje (pierwsza instalacja)
    if not db_path.exists():
        print(f"[DB] Baza nie istnieje - tworzenie nowej...")
        
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Nie można utworzyć folderu dla bazy: {e}")
        
        # Stwórz tabele z najnowszą strukturą
        Base.metadata.create_all(bind=engine)
        
        print(f"[DB] Baza danych utworzona")
        print(f"[DB] Wszystkie tabele mają najnowszą strukturę (v{settings.VERSION})")
        
        # Inicjalizuj system migracji i oznacz wersję
        from migrations import init_migration_tracking, set_db_version
        init_migration_tracking()
        set_db_version(settings.VERSION)
        
        print("[DB] ═══════════════════════════════════════")
        return
    
    # SCENARIUSZ 2: Baza istnieje (aktualizacja lub kolejne uruchomienie)
    print(f"[DB] Baza istnieje - sprawdzanie aktualizacji...")
    
    # Inicjalizuj system migracji (stwórz migration_history jeśli nie istnieje)
    from migrations import init_migration_tracking
    init_migration_tracking()
    
    # Uruchom pending migracje
    run_pending_migrations()
    
    print(f"[DB]Baza danych jest aktualna (v{settings.VERSION})")
    print("[DB] ═══════════════════════════════════════")

def _is_path_accessible(path: Path) -> bool:
    """Sprawdź czy ścieżka jest dostępna do zapisu"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        # Spróbuj utworzyć i usunąć testowy plik
        test_file = path / ".db_access_test"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception as e:
        print(f"[DB] Path not accessible: {e}")
        return False

def run_pending_migrations():
    """Uruchom wszystkie migracje które jeszcze nie zostały wykonane"""
    from migrations import is_migration_executed, get_db_version, set_db_version
    from migrations.registry import MIGRATIONS
    import importlib
    
    db_version = get_db_version()
    app_version = settings.VERSION
    
    print(f"[DB] Database version: {db_version}")
    print(f"[DB] Application version: {app_version}")
    
    # Znajdź pending migracje
    pending = []
    
    for migration_id, min_version, description in MIGRATIONS:
        if not is_migration_executed(migration_id):
            pending.append((migration_id, min_version, description))
    
    if not pending:
        print("[DB] No pending migrations")
        # Zaktualizuj wersję bazy do wersji aplikacji
        if db_version != app_version:
            set_db_version(app_version)
            print(f"[DB] Database version updated: {db_version} → {app_version}")
        return
    
    print(f"[DB] Found {len(pending)} pending migrations:")
    
    for migration_id, min_version, description in pending:
        print(f"[DB] {migration_id} (v{min_version})")
        print(f"[DB]      {description}")
        
        try:
            migration_module = importlib.import_module(f"migrations.{migration_id}")
            migration_module.upgrade()
            print(f"[DB] Completed")
            
        except Exception as e:
            print(f"[DB] ERROR: {e}")
            raise RuntimeError(f"Migration {migration_id} failed: {e}")
    
    # Zaktualizuj wersję bazy
    set_db_version(app_version)
    print(f"[DB] All migrations completed")
    print(f"[DB] Database updated to v{app_version}")