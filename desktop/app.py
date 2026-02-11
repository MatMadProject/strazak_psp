import webview
import uvicorn
import sys
import os
from threading import Thread
from pathlib import Path
import time
import requests
import importlib.util
from logger import setup_logger

logger = setup_logger()

# Funkcja do znalezienia ścieżki zasobów (działa z PyInstaller)
def get_resource_path(relative_path):
    """Pobierz absolutną ścieżkę do zasobu - działa z PyInstaller"""
    try:
        # PyInstaller tworzy folder tymczasowy i zapisuje ścieżkę w _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Normalny tryb development
        base_path = Path(__file__).parent.parent
    
    return Path(base_path) / relative_path

# Określ ścieżkę do backendu
backend_path = get_resource_path("backend")
sys.path.insert(0, str(backend_path))

# Dynamiczny import backend/main.py
backend_main_file = backend_path / "main.py"

if not backend_main_file.exists():
    raise FileNotFoundError(
        f"Nie znaleziono backend/main.py w: {backend_main_file}\n"
        f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'nie ustawione')}\n"
        f"Zawartość katalogu: {list(Path(sys._MEIPASS).iterdir()) if hasattr(sys, '_MEIPASS') else 'brak'}"
    )

spec = importlib.util.spec_from_file_location("backend_main", backend_main_file)
backend_module = importlib.util.module_from_spec(spec)
sys.modules['backend_main'] = backend_module
spec.loader.exec_module(backend_module)
fastapi_app = backend_module.app

class DesktopApp:
    def __init__(self):
        self.server_thread = None
        self.server = None
        self.backend_ready = False
        self.port = 8000
    
    def start_backend(self):
        """Uruchom FastAPI w osobnym wątku"""
        print("Uruchamianie backendu...")
        
        config = uvicorn.Config(
            fastapi_app,
            host="127.0.0.1",
            port=self.port,
            log_level="info",
            access_log=True
        )
        self.server = uvicorn.Server(config)
        
        def run_server():
            self.server.run()
        
        self.server_thread = Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Poczekaj aż backend będzie gotowy
        self.wait_for_backend()
    
    def wait_for_backend(self):
        """Poczekaj aż backend odpowiada"""
        max_attempts = 30
        url = f"http://127.0.0.1:{self.port}/health"
        
        print("Czekam na backend...")
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    self.backend_ready = True
                    print("Backend gotowy!")
                    return
            except Exception:
                pass
            time.sleep(0.2)
        
        raise Exception("Backend nie uruchomił się w czasie 6 sekund")
    
    def get_frontend_url(self):
        """Zwróć URL do frontendu"""
        # W produkcji (spakowanej wersji) React build jest serwowany przez FastAPI
        # W developmencie możesz zmienić na http://localhost:3000
        return f"http://127.0.0.1:{self.port}"
    
    def shutdown(self):
        """Zamknij serwer przy zamykaniu aplikacji"""
        print("Zamykanie aplikacji...")
        if self.server:
            self.server.should_exit = True

def show_error(message):
    """Pokaż błąd użytkownikowi"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Błąd uruchomienia", message)
    except:
        print(f"BŁĄD: {message}")

def main():
    try:
        logger.info("=" * 50)
        logger.info("  STRAZAK APP")
        logger.info("=" * 50)
        print("=" * 50)
        print("  STRAZAK APP")
        print("=" * 50)
        
        app_instance = DesktopApp()
        
        # KROK 1: Uruchom backend
        app_instance.start_backend()
        
        # KROK 2: Pobierz URL frontendu
        frontend_url = app_instance.get_frontend_url()
        print(f"Ładowanie interfejsu z: {frontend_url}")
        
        # KROK 3: Utwórz okno aplikacji
        window = webview.create_window(
            'Strazak App',
            frontend_url,
            width=1400,
            height=900,
            resizable=True,
            background_color='#FFFFFF',
            confirm_close=False
        )
        
        # KROK 4: Uruchom aplikację
        print("Aplikacja uruchomiona!")
        print("=" * 50)
        webview.start()
        
        # KROK 5: Po zamknięciu okna
        app_instance.shutdown()
        print("Aplikacja zamknięta")
        
    except Exception as e:
        error_msg = (
            f"Nie udało się uruchomić aplikacji:\n\n{str(e)}\n\n"
            f"Sprawdź czy:\n"
            f"1. Backend jest poprawnie zainstalowany\n"
            f"2. Port 8000 nie jest zajęty\n"
            f"3. Masz wszystkie wymagane biblioteki"
        )
        print(f"\nBŁĄD: {error_msg}")
        show_error(error_msg)
        sys.exit(1)

if __name__ == '__main__':
    main()