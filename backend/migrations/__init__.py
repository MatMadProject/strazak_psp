"""
Prosty system śledzenia migracji z wersjonowaniem
"""
from sqlalchemy import text, Table, Column, String, DateTime, MetaData
from datetime import datetime
from database import engine

metadata = MetaData()

migration_history = Table(
    'migration_history',
    metadata,
    Column('id', String, primary_key=True),
    Column('name', String),
    Column('executed_at', DateTime, default=datetime.utcnow)
)

db_version_table = Table(
    'db_version',
    metadata,
    Column('version', String, primary_key=True),
    Column('updated_at', DateTime, default=datetime.utcnow)
)

def init_migration_tracking():
    """Stwórz tabele śledzące migracje i wersję bazy"""
    metadata.create_all(engine)

def mark_migration_executed(migration_id: str, migration_name: str):
    """Oznacz migrację jako wykonaną"""
    with engine.connect() as conn:
        conn.execute(
            migration_history.insert().values(
                id=migration_id,
                name=migration_name,
                executed_at=datetime.utcnow()
            )
        )
        conn.commit()

def unmark_migration_executed(migration_id: str):
    """Usuń migrację z historii (dla rollback)"""
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM migration_history WHERE id = :id"),
            {"id": migration_id}
        )
        conn.commit()

def is_migration_executed(migration_id: str) -> bool:
    """Sprawdź czy migracja została już wykonana"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM migration_history WHERE id = :id"),
                {"id": migration_id}
            ).scalar()
            return result > 0
    except:
        return False

def get_executed_migrations():
    """Pobierz listę wykonanych migracji"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM migration_history ORDER BY executed_at"))
            return result.fetchall()
    except:
        return []

def get_db_version() -> str:
    """Pobierz wersję bazy danych"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version FROM db_version LIMIT 1")).scalar()
            return result if result else "0.0.0"
    except:
        return "0.0.0"

def set_db_version(version: str):
    """Ustaw wersję bazy danych"""
    with engine.connect() as conn:
        # Usuń starą wersję
        conn.execute(text("DELETE FROM db_version"))
        
        # Dodaj nową
        conn.execute(
            text("INSERT INTO db_version (version, updated_at) VALUES (:version, :updated_at)"),
            {"version": version, "updated_at": datetime.utcnow()}
        )
        conn.commit()