"""
Migracja 002: Dodanie tabeli hazardous_degrees (Stopnie Szkodliwości)
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database import engine
from sqlalchemy import text


def upgrade():
    """Utwórz tabelę hazardous_degrees"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hazardous_degrees (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                stopien    INTEGER NOT NULL,
                punkt      INTEGER NOT NULL,
                opis       TEXT    NOT NULL,
                uwagi      TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Indeks na stopien + punkt — najczęstszy filtr
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_hazardous_degrees_stopien_punkt
            ON hazardous_degrees (stopien, punkt)
        """))

        conn.commit()

    # Oznacz migrację jako wykonaną
    from migrations import mark_migration_executed
    mark_migration_executed(
        "002_hazardous_degrees_add_20260301",
        "Dodanie tabeli hazardous_degrees"
    )

    print("[MIGRATION] 002_hazardous_degrees_add: OK")


def downgrade():
    """Usuń tabelę hazardous_degrees (rollback)"""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS hazardous_degrees"))
        conn.commit()