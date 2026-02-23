"""
Tworzy czystą bazę danych do pakowania w installer
"""
from datetime import datetime
import shutil
import sys
from pathlib import Path

# Dodaj backend do path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, inspect
from database import Base
import shutil

# WAŻNE: Importuj WSZYSTKIE modele jawnie
from models import (
    Firefighter,
    ImportedFile,
    SWDRecord,
    # Dodaj tutaj inne modele jeśli są
)

def create_fresh_database(output_path: str = None):
    """
    Stwórz czystą bazę danych z pustymi tabelami
    
    Args:
        output_path: Gdzie zapisać bazę (domyślnie: data/app.db)
    """
    
    if output_path is None:
        output_path = Path(__file__).parent.parent / "data" / "app.db"
    else:
        output_path = Path(output_path)
    
    print("=" * 70)
    print("  TWORZENIE CZYSTEJ BAZY DANYCH")
    print("=" * 70)
    print()
    
    # Backup starej bazy jeśli istnieje
    if output_path.exists():
    # Format: app_backup_20260221_143025.db
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = output_path.parent / f"{output_path.stem}_backup_{timestamp}{output_path.suffix}"
        
        print(f"📦 Tworzę backup: {backup_path.name}")
        shutil.copy2(output_path, backup_path)
        output_path.unlink()
        print(f"✓ Stara baza zapisana jako backup")
    
    # Stwórz folder jeśli nie istnieje
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Debug - sprawdź co jest w metadata
    print(f"\nZnalezione modele w Base.metadata:")
    for table in Base.metadata.tables:
        print(f"   • {table}")
    
    if not Base.metadata.tables:
        print("\nBŁĄD: Brak modeli w Base.metadata!")
        print("Sprawdź czy wszystkie modele są poprawnie zdefiniowane.")
        return None
    
    # Stwórz nową bazę
    temp_engine = create_engine(f"sqlite:///{output_path}")
    
    print(f"\nTworzę czystą bazę: {output_path}")
    Base.metadata.create_all(bind=temp_engine)
    
    # Weryfikuj
    inspector = inspect(temp_engine)
    tables = inspector.get_table_names()
    
    print(f"\nUtworzono {len(tables)} tabel:")
    for table in tables:
        # Pokaż kolumny każdej tabeli
        columns = inspector.get_columns(table)
        print(f"   • {table} ({len(columns)} kolumn)")
        if len(sys.argv) > 1 and sys.argv[1] == "-v":
            for col in columns:
                print(f"      - {col['name']} ({col['type']})")
    
    print(f"\nCzysta baza gotowa: {output_path}")
    print(f"\nRozmiar: {output_path.stat().st_size / 1024:.2f} KB")
    print()
    print("=" * 70)
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ["-v", "--verbose"]:
        output = sys.argv[1]
    else:
        output = None
    
    result = create_fresh_database(output)
    
    if result is None:
        print("\nTworzenie bazy nie powiodło się!")
        sys.exit(1)