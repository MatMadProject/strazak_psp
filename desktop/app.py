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


def get_resource_path(relative_path):
    """Pobierz absolutną ścieżkę do zasobu - działa z PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).parent.parent
    return Path(base_path) / relative_path


# Określ ścieżkę do backendu
backend_path = get_resource_path("backend")
sys.path.insert(0, str(backend_path))

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


# ─── SPLASH SCREEN ───────────────────────────────────────────────────────────

class SplashScreen:
    """
    Splash screen z logo jako tłem (600x400, proporcje 3:2).
    Plik splash.png musi być w tym samym katalogu co app.py
    (lub spakowany przez PyInstaller obok pliku exe).
    """
    def __init__(self):
        self.root = None
        self.label_status = None
        self.canvas = None
        self.progress_bar = None

    def _get_splash_image_path(self) -> Path:
        try:
            base = Path(sys._MEIPASS)
        except AttributeError:
            base = Path(__file__).parent
        return base / "splash.png"

    def show(self):
        import tkinter as tk
        from PIL import Image, ImageTk

        self.root = tk.Tk()
        self.root.overrideredirect(True)        # brak ramki
        self.root.attributes("-topmost", True)  # zawsze na wierzchu

        W, H = 600, 400
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - W) // 2
        y = (sh - H) // 2
        self.root.geometry(f"{W}x{H}+{x}+{y}")

        # Tło — logo
        splash_path = self._get_splash_image_path()
        img = Image.open(splash_path).resize((W, H), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(img)  # trzymaj referencję

        bg = tk.Label(self.root, image=self._photo, bd=0)
        bg.place(x=0, y=0, relwidth=1, relheight=1)

        # Półprzezroczysty pasek na dole (canvas jako tło paska)
        bar_h = 48
        bar_canvas = tk.Canvas(
            self.root, width=W, height=bar_h,
            bg="#0a1628", highlightthickness=0
        )
        bar_canvas.place(x=0, y=H - bar_h)
        bar_canvas.create_rectangle(0, 0, W, bar_h, fill="#0a1628", outline="")

        # Tekst statusu
        self.label_status = tk.Label(
            self.root, text="Uruchamianie...",
            font=("Arial", 9), bg="#0a1628", fg="#bdc3c7"
        )
        self.label_status.place(x=12, y=H - bar_h + 6)

        # Pasek postępu
        self.canvas = tk.Canvas(
            self.root, width=W - 24, height=5,
            bg="#1a3a5c", highlightthickness=0
        )
        self.canvas.place(x=12, y=H - bar_h + 28)
        self.progress_bar = self.canvas.create_rectangle(
            0, 0, 0, 5, fill="#3498db", outline=""
        )

        self.root.update()

    def set_status(self, text: str, progress: float = None):
        if not self.root:
            return
        try:
            self.label_status.config(text=text)
            if progress is not None:
                bar_w = 576   # W - 24
                self.canvas.coords(self.progress_bar, 0, 0, bar_w * progress, 5)
            self.root.update()
        except Exception:
            pass

    def close(self):
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
            self.root = None


# ─── DESKTOP APP ─────────────────────────────────────────────────────────────

class DesktopApp:
    def __init__(self):
        self.server_thread = None
        self.server = None
        self.backend_ready = False
        self.port = 8000

    def start_backend(self):
        """Uruchom FastAPI w osobnym wątku"""
        logger.info("Uruchamianie backendu...")

        config = uvicorn.Config(
            fastapi_app,
            host="127.0.0.1",
            port=self.port,
            log_level="warning",   # mniej szumu w logach
            access_log=False,
        )
        self.server = uvicorn.Server(config)

        self.server_thread = Thread(target=self.server.run, daemon=True)
        self.server_thread.start()

        self.wait_for_backend()

    def wait_for_backend(self):
        """Poczekaj aż backend odpowiada"""
        max_attempts = 30
        url = f"http://127.0.0.1:{self.port}/health"

        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    self.backend_ready = True
                    logger.info("Backend gotowy!")
                    return
            except Exception:
                pass
            time.sleep(0.2)

        raise Exception("Backend nie uruchomił się w czasie 6 sekund")

    def get_frontend_url(self):
        return f"http://127.0.0.1:{self.port}"

    def shutdown(self):
        """
        Zamknij serwer i zakończ cały proces.
        Wywołane po zamknięciu okna pywebview — bez tego
        proces zostaje w tle z zajętym portem.
        """
        logger.info("Zamykanie aplikacji...")
        if self.server:
            self.server.should_exit = True
            # Daj chwilę na czysty shutdown uvicorn
            time.sleep(0.5)
        # Wymuś zakończenie całego procesu
        os._exit(0)


def show_error(message):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Błąd uruchomienia", message)
        root.destroy()
    except Exception:
        print(f"BŁĄD: {message}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    splash = SplashScreen()

    try:
        logger.info("=" * 50)
        logger.info("  STRAZAK APP — START")
        logger.info("=" * 50)

        # Splash — krok 1
        splash.show()
        splash.set_status("Inicjalizacja...", 0.1)

        app_instance = DesktopApp()

        # Splash — krok 2
        splash.set_status("Uruchamianie serwera...", 0.3)
        app_instance.start_backend()

        # Splash — krok 3
        splash.set_status("Ładowanie interfejsu...", 0.8)
        frontend_url = app_instance.get_frontend_url()

        # Utwórz okno pywebview (jeszcze nie pokazane)
        window = webview.create_window(
            'Strażak',
            frontend_url,
            width=1400,
            height=900,
            resizable=True,
            background_color='#FFFFFF',
            confirm_close=False,
        )

        splash.set_status("Gotowe!", 1.0)
        time.sleep(0.4)   # krótka pauza żeby user zobaczył "Gotowe!"
        splash.close()

        logger.info("Aplikacja uruchomiona!")

        # Uruchom pywebview — blokuje do zamknięcia okna
        webview.start()

        # Po zamknięciu okna — shutdown + os._exit
        app_instance.shutdown()

    except Exception as e:
        splash.close()
        error_msg = (
            f"Nie udało się uruchomić aplikacji:\n\n{str(e)}\n\n"
            f"Sprawdź czy:\n"
            f"1. Backend jest poprawnie zainstalowany\n"
            f"2. Port 8000 nie jest zajęty\n"
            f"3. Masz wszystkie wymagane biblioteki"
        )
        logger.exception("Błąd uruchomienia aplikacji")
        show_error(error_msg)
        sys.exit(1)


if __name__ == '__main__':
    main()