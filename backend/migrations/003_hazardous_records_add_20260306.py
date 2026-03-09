"""
Migracja 003: Dodanie tabeli hazardous_records (Dodatek Szkodliwy)
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database import engine
from sqlalchemy import text


def upgrade():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hazardous_records (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id                 INTEGER NOT NULL
                                        REFERENCES imported_files(id) ON DELETE CASCADE,
                jednostka               VARCHAR(255),
                nazwisko_imie           VARCHAR(255),
                stopien                 VARCHAR(100),
                data_przyjecia          VARCHAR(50),
                p                       VARCHAR(10),
                mz                      VARCHAR(10),
                af                      VARCHAR(10),
                nr_meldunku             VARCHAR(100),
                funkcja                 VARCHAR(100),
                czas_od                 VARCHAR(50),
                czas_do                 VARCHAR(50),
                czas_udzialu            VARCHAR(50),
                dodatek_szkodliwy       VARCHAR(10),
                stopien_szkodliwosci    VARCHAR(50),
                aktualizowal_szkod      VARCHAR(255),
                data_aktualizacji_szkod VARCHAR(50),
                opis_st_szkodliwosci    TEXT,
                hazardous_degree_id     INTEGER
                                        REFERENCES hazardous_degrees(id) ON DELETE SET NULL,
                created_at              VARCHAR(50),
                updated_at              VARCHAR(50)
            )
        """))

        # Indeks na file_id — najczęstszy filtr
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_hazardous_records_file_id
            ON hazardous_records (file_id)
        """))

        # Indeks na nazwisko_imie — filtrowanie po osobie
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_hazardous_records_nazwisko
            ON hazardous_records (nazwisko_imie)
        """))

        # Indeks na hazardous_degree_id — JOIN ze stopniami
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_hazardous_records_degree
            ON hazardous_records (hazardous_degree_id)
        """))

        conn.commit()

    from migrations import mark_migration_executed
    mark_migration_executed(
        "003_hazardous_records_add_20260306",
        "Dodanie tabeli hazardous_records (Dodatek Szkodliwy)"
    )
    print("[MIGRATION] 003_hazardous_records_add: OK")


def downgrade():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS hazardous_records"))
        conn.commit()