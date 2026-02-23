"""
Prosty system śledzenia migracji
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

def init_migration_tracking():
    """Stwórz tabelę śledzącą migracje"""
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
    print(f"Marked as executed: {migration_id}")
def unmark_migration_executed(migration_id: str):
    """Usuń migrację z historii (dla rollback)"""
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM migration_history WHERE id = :id"),
            {"id": migration_id}
        )
        conn.commit()
    print(f"Unmarked: {migration_id}")
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
        # Tabela migration_history nie istnieje
        return False

def get_executed_migrations():
    """Pobierz listę wykonanych migracji"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM migration_history ORDER BY executed_at"))
            return result.fetchall()
    except:
        return []