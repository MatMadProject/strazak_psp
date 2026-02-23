"""
Wyświetl listę wykonanych migracji z kolorami
"""
import sys
from pathlib import Path

# Dodaj backend do path
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrations import get_executed_migrations, init_migration_tracking
from datetime import datetime

# Kolory ANSI (działa w większości terminali)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color):
    """Wydrukuj kolorowy tekst"""
    print(f"{color}{text}{Colors.RESET}")

def list_migrations(verbose=False):
    """
    Wyświetl listę wykonanych migracji
    
    Args:
        verbose: Czy pokazać szczegółowe informacje
    """
    
    print_colored("=" * 70, Colors.BOLD)
    print_colored("  📋 WYKONANE MIGRACJE", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 70, Colors.BOLD)
    print()
    
    try:
        # Inicjalizuj tracking jeśli nie istnieje
        init_migration_tracking()
        
        # Pobierz migracje
        migrations = get_executed_migrations()
        
        if not migrations:
            print_colored("⚠️  Brak wykonanych migracji", Colors.YELLOW)
            print()
            print("💡 Uruchom pierwszą migrację:")
            print("   python migrations/001_nazwa_migracji.py")
            print()
            return
        
        print_colored(f"✅ Znaleziono {len(migrations)} migracji:", Colors.GREEN)
        print()
        
        if verbose:
            # Szczegółowy widok
            for idx, migration in enumerate(migrations, 1):
                migration_id = migration[0]
                migration_name = migration[1]
                executed_at = migration[2]
                
                if isinstance(executed_at, str):
                    date_str = executed_at
                elif isinstance(executed_at, datetime):
                    date_str = executed_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str = str(executed_at)
                
                print_colored(f"[{idx}] {migration_id}", Colors.BOLD + Colors.BLUE)
                print(f"    Nazwa: {migration_name}")
                print(f"    Data:  {date_str}")
                print()
        else:
            # Tabelka
            print(f"{'#':<4} {'ID':<32} {'Nazwa':<38} {'Data':<20}")
            print_colored("-" * 94, Colors.CYAN)
            
            for idx, migration in enumerate(migrations, 1):
                migration_id = migration[0]
                migration_name = migration[1]
                executed_at = migration[2]
                
                if isinstance(executed_at, str):
                    date_str = executed_at
                elif isinstance(executed_at, datetime):
                    date_str = executed_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str = str(executed_at)
                
                # Skróć nazwę jeśli za długa
                if len(migration_name) > 38:
                    migration_name = migration_name[:35] + "..."
                
                print(f"{idx:<4} {migration_id:<32} {migration_name:<38} {date_str:<20}")
        
        print()
        print_colored("=" * 70, Colors.BOLD)
        
    except Exception as e:
        print_colored(f"❌ Błąd: {e}", Colors.RED)
        print()
        print("Tabela migration_history prawdopodobnie nie istnieje.")
        print("Uruchom pierwszą migrację aby ją utworzyć.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wyświetl wykonane migracje")
    parser.add_argument('-v', '--verbose', action='store_true', help="Szczegółowy widok")
    
    args = parser.parse_args()
    
    list_migrations(verbose=args.verbose)