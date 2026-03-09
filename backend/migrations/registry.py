"""
Rejestr wszystkich migracji z informacją o wersji aplikacji
"""

MIGRATIONS = [
    # Format: (migration_id, min_version, description)
    # min_version = minimalna wersja aplikacji wymagana do tej migracji
    
     (
        "001_swd_record_add_20260221",
        "0.1.0",
        "Dodanie kolumny specjalistyczne do swd_records"
    ),
    (
        "002_hazardous_degrees_add_20260301",
        "0.3.3",
        "Dodanie tabeli hazardous_degrees (Stopnie Szkodliwości)"
    ),
    (
        "003_hazardous_records_add_20260306",
        "0.4.0",
        "Dodanie tabeli hazardous_records (Dodatek szkodliwy)"
    ),
    # Przyszłe migracje:
    # ("003_reports_table", "0.4.0", "Dodanie tabeli raportów"),
]

def get_migrations_for_version(from_version: str, to_version: str):
    """
    Zwróć migracje które trzeba wykonać przy aktualizacji
    
    Args:
        from_version: Aktualna wersja bazy (np. "0.2.0")
        to_version: Docelowa wersja aplikacji (np. "0.3.0")
    
    Returns:
        Lista migration_id do wykonania
    """
    from packaging import version
    
    to_exec = []
    
    for migration_id, min_version, description in MIGRATIONS:
        # Wykonaj migrację jeśli jest między from_version a to_version
        if version.parse(from_version) < version.parse(min_version) <= version.parse(to_version):
            to_exec.append(migration_id)
    
    return to_exec