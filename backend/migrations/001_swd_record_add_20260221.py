"""
Migracja: Dodanie pola specjalistyczne do tabeli swd_record
Data: 2026-02-21
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from database import engine
from migrations import init_migration_tracking, mark_migration_executed, is_migration_executed, unmark_migration_executed

MIGRATION_ID = "001_swd_record_add_20260221"
MIGRATION_NAME = "Add specjalistyczne fields to swd_record"
def upgrade():
    # Inicjalizuj tracking
    init_migration_tracking()
    
    # Sprawdź czy już wykonano
    if is_migration_executed(MIGRATION_ID):
        print(f"Migration {MIGRATION_ID} already executed, skipping")
        return

    print(f"=== MIGRATION: {MIGRATION_NAME} ===")

    """Dodaj nowe pola"""
    migrations = [
        "ALTER TABLE swd_records ADD COLUMN specjalistyczne VARCHAR;"
    ]
    
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                print(f"Executed: {sql}")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print(f"Skipped (already exists): {sql}")
                else:
                    print(f"Error: {e}")
                    raise
        conn.commit()

    # Oznacz jako wykonaną
    mark_migration_executed(MIGRATION_ID, MIGRATION_NAME)

    print("Migration completed successfully")
   

def downgrade():
    """Cofnij zmiany (opcjonalnie)"""
    print(f"=== ROLLBACK: {MIGRATION_NAME} ===")
    migrations = [
        "ALTER TABLE swd_record DROP COLUMN specjalistyczne;"
    ]
    
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                print(f"Rolled back: {sql}")
            except Exception as e:
                print(f"Error: {e}")
        conn.commit()
    
    # Usuń z historii migracji
    unmark_migration_executed(MIGRATION_ID)
    
    print("Rollback completed")

if __name__ == "__main__":
    print("=" * 60)
    print(f"  MIGRATION: {MIGRATION_ID}")
    print("=" * 60)
    print()
    print(f"Name: {MIGRATION_NAME}")
    print()
    print("Options:")
    print("  1. Run migration (upgrade)")
    print("  2. Rollback migration (downgrade)")
    print("  3. Cancel")
    print()
    
    choice = input("Choose option (1/2/3): ")
    
    if choice == "1":
        upgrade()
    elif choice == "2":
        downgrade()
    else:
        print("❌ Cancelled")
