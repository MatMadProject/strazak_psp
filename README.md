# SWD Desktop App

Aplikacja desktop do importu i zarządzania danymi SWD z plików Excel.

## 🚀 Szybki start

### Wymagania

- **Python 3.9+** - [Pobierz tutaj](https://www.python.org/)
- **Node.js 16+** - [Pobierz tutaj](https://nodejs.org/)
- **Git** (opcjonalnie)

### Instalacja

1. **Sklonuj/pobierz projekt**

```bash
cd swd-desktop-app
```

2. **Uruchom setup projektu**

```bash
cd scripts
setup_project.bat
```

To zainstaluje wszystkie wymagane zależności.

## 💻 Development

### Uruchomienie w trybie deweloperskim

```bash
cd scripts
dev_start.bat
```

To uruchomi:

- Backend (FastAPI) na `http://127.0.0.1:8000`
- Frontend (React) na `http://localhost:3000`

Frontend automatycznie otworzy się w przeglądarce.

### Testowanie biblioteki zestawienie-udzialu-swd

⚠️ **WAŻNE**: Upewnij się, że biblioteka `zestawienie-udzialu-swd` jest zainstalowana:

```bash
pip install git+https://github.com/MatMadProject/zestawienie-udzialu-swd.git
```

Następnie dostosuj kod w `backend/services/excel_processor.py` do API biblioteki.

## 📦 Budowanie aplikacji desktop

### Krok 1: Build aplikacji

```bash
cd scripts
build_desktop.bat
```

To stworzy:

- `desktop/dist/SWD-DesktopApp.exe` - gotowa aplikacja

### Krok 2: Stwórz installer (opcjonalnie)

Najpierw zainstaluj [Inno Setup](https://jrsoftware.org/isdl.php).

Następnie:

```bash
cd scripts
create_installer.bat
```

To stworzy:

- `installer/output/SWD-DesktopApp-Setup-v1.0.0.exe` - instalator

## 📁 Struktura projektu

```
swd-desktop-app/
├── backend/          # FastAPI backend
│   ├── main.py
│   ├── models/
│   ├── routes/
│   └── services/
├── frontend/         # React frontend
│   ├── src/
│   ├── public/
│   └── build/
├── desktop/          # PyWebView wrapper
│   └── main.py
├── installer/        # Inno Setup scripts
├── scripts/          # Build scripts
└── data/            # Baza danych (SQLite)
```

## 🔧 Konfiguracja

### Backend (backend/config.py)

- `DATABASE_URL` - Ścieżka do bazy danych
- `UPLOAD_DIR` - Folder na przesłane pliki
- `MAX_UPLOAD_SIZE` - Maksymalny rozmiar pliku

### Frontend (frontend/src/services/api.js)

- `API_URL` - URL backendu (domyślnie: http://127.0.0.1:8000)

## 🗄️ Baza danych

Aplikacja używa **SQLite** dla wersji desktop (plik: `data/app.db`).

### Modele:

- **ImportedFile** - Zaimportowane pliki Excel
- **SWDRecord** - Pojedyncze rekordy z danych SWD

## 🌐 Przejście na Web App

Gdy będziesz gotowy do wersji web:

1. **Backend**:
   - Zmień `DATABASE_URL` na PostgreSQL
   - Deploy na AWS/Heroku/DigitalOcean

2. **Frontend**:
   - `npm run build`
   - Deploy na Netlify/Vercel

3. **Dodaj autentykację** (JWT, OAuth)

## 📱 Przejście na Mobile App

Backend pozostaje ten sam! Tylko stwórz nowy frontend w:

- React Native
- Flutter

## 🐛 Rozwiązywanie problemów

### Błąd: "Port 8000 zajęty"

Zmień port w `backend/main.py` i `desktop/main.py`.

### Błąd: "Brak modułu zestawienie_udzialu_swd"

Zainstaluj bibliotekę:

```bash
pip install git+https://github.com/MatMadProject/zestawienie-udzialu-swd.git
```

### Błąd buildu React: "Node memory exceeded"

Zwiększ pamięć Node.js:

```bash
set NODE_OPTIONS=--max-old-space-size=4096
npm run build
```

### Aplikacja nie uruchamia się po spakowaniu

Sprawdź logi w konsoli. Upewnij się, że:

- Wszystkie ścieżki są relatywne
- Wszystkie zależności są uwzględnione w PyInstaller

## 📝 TODO / Roadmap

- [ ] Integracja z biblioteką zestawienie-udzialu-swd
- [ ] Eksport danych do Excel/PDF
- [ ] Wykresy i wizualizacje
- [ ] Filtry zaawansowane
- [ ] Import wsadowy (wiele plików)
- [ ] Backup/restore bazy danych
- [ ] Autentykacja użytkowników (dla web)
- [ ] API documentation (Swagger)

## 📄 Licencja

MIT License - możesz używać kodu w dowolny sposób.

## 🤝 Kontakt

W razie pytań lub problemów:

- GitHub Issues
- Email: support@twojafirma.pl

---

**Wersja**: 1.0.0  
**Data**: 2024
