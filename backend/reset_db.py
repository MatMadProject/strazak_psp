"""
Reset bazy danych - usuwa wszystkie dane i tworzy czyste tabele
UWAGA: To usuwa WSZYSTKIE dane!
"""
from database import engine, Base
from models import *
import os
from pathlib import Path

def reset_database():
    """Usuń wszystkie tabele i stwórz na nowo"""
    
    print("=" * 60)
    print("  RESET BAZY DANYCH")
    print("=" * 60)
    print()
    print(" UWAGA: To usunie WSZYSTKIE dane z bazy!")
    print()
    
    response = input("Czy na pewno chcesz kontynuować? (wpisz 'TAK'): ")
    
    if response != "TAK":
        print("Anulowano")
        return
    
    print()
    print("[1/3] Usuwanie tabel...")
    Base.metadata.drop_all(bind=engine)
    print("Tabele usunięte")
    
    print("[2/3] Tworzenie nowych tabel...")
    Base.metadata.create_all(bind=engine)
    print("Tabele utworzone")
    
    print("[3/3] Weryfikacja...")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Utworzono {len(tables)} tabel: {', '.join(tables)}")
    
    print()
    print("=" * 60)
    print("BAZA DANYCH ZRESETOWANA")
    print("=" * 60)

if __name__ == "__main__":
    reset_database()