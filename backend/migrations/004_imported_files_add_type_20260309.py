"""
Migracja 004: Dodanie kolumny file_type do imported_files
Wartości: "departures" | "hazardous"
Domyślnie "departures" — istniejące rekordy to pliki Wyjazdów.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database import engine
from sqlalchemy import text


def upgrade():
    with engine.connect() as conn:
        # Sprawdź czy kolumna już istnieje (SQLite nie ma IF NOT EXISTS dla ALTER)
        result = conn.execute(text("PRAGMA table_info(imported_files)"))
        columns = [row[1] for row in result.fetchall()]

        if "file_type" not in columns:
            conn.execute(text("""
                ALTER TABLE imported_files
                ADD COLUMN file_type VARCHAR(50) DEFAULT 'departures'
            """))
            conn.commit()
            print("[MIGRATION] 004: Dodano kolumnę file_type do imported_files")
        else:
            print("[MIGRATION] 004: Kolumna file_type już istnieje — pomijam")

    from migrations import mark_migration_executed
    mark_migration_executed(
        "004_imported_files_add_type_20260309",
        "Dodanie kolumny file_type do imported_files"
    )
    print("[MIGRATION] 004_imported_files_add_type: OK")


def downgrade():
    # SQLite nie wspiera DROP COLUMN w starszych wersjach
    print("[MIGRATION] 004 downgrade: SQLite nie wspiera DROP COLUMN — pomiń")