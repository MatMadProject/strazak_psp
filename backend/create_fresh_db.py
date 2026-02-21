"""
Tworzy czystą bazę danych do pakowania w installer
"""
from database import engine, Base
from models import *
from pathlib import Path
import shutil

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
    
    # Backup starej bazy jeśli istnieje
    if output_path.exists():
        backup_path = output_path.parent / f"{output_path.stem}_backup{output_path.suffix}"
        print(f"Tworzę backup: {backup_path}")
        shutil.copy2(output_path, backup_path)
        output_path.unlink()
    
    # Stwórz folder jeśli nie istnieje
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Stwórz nową bazę
    from sqlalchemy import create_engine
    temp_engine = create_engine(f"sqlite:///{output_path}")
    
    print(f"Tworzę czystą bazę: {output_path}")
    Base.metadata.create_all(bind=temp_engine)
    
    # Weryfikuj
    from sqlalchemy import inspect
    inspector = inspect(temp_engine)
    tables = inspector.get_table_names()
    
    print(f"Utworzono {len(tables)} tabel:")
    for table in tables:
        print(f"   • {table}")
    
    print(f"\nCzysta baza gotowa: {output_path}")
    print(f"Rozmiar: {output_path.stat().st_size / 1024:.2f} KB")
    
    return output_path

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        output = sys.argv[1]
    else:
        output = None
    
    create_fresh_database(output)