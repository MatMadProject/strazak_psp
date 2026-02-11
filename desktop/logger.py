import sys
import logging
from pathlib import Path
from datetime import datetime

def setup_logger():
    """Skonfiguruj logowanie do pliku dla aplikacji desktopowej"""
    
    # Katalog logów w katalogu użytkownika
    if sys.platform == "win32":
        import os
        log_dir = Path(os.environ.get('APPDATA', Path.home())) / 'StrazakDesktopApp' / 'logs'
    else:
        log_dir = Path.home() / '.local' / 'share' / 'StrazakDesktopApp' / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Plik logu z datą
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Konfiguracja
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # Nadal wypisuj do konsoli jeśli jest
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"📝 Log file: {log_file}")
    
    return logger