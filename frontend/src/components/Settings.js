import React, { useState, useEffect } from "react";
import { settingsAPI } from "../services/api";
import "./Settings.css";

function Settings({ isDesktop }) {
  const [settings, setSettings] = useState(null);
  const [currentDatabase, setCurrentDatabase] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [databaseType, setDatabaseType] = useState("local");
  const [databasePath, setDatabasePath] = useState("");
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadSettings();
    loadCurrentDatabase();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await settingsAPI.getSettings();
      setSettings(data);
      setDatabaseType(data.database.type);
      setDatabasePath(data.database.path);
    } catch (error) {
      console.error("Błąd ładowania ustawień:", error);
      setMessage({ type: "error", text: "Nie udało się załadować ustawień" });
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentDatabase = async () => {
    try {
      const data = await settingsAPI.getCurrentDatabase();
      setCurrentDatabase(data);
    } catch (error) {
      console.error("Błąd ładowania info o bazie:", error);
    }
  };

  const handleSave = async () => {
    if (!databasePath.trim()) {
      setMessage({ type: "error", text: "Ścieżka do bazy nie może być pusta" });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      const response = await settingsAPI.updateSettings({
        database: {
          type: databaseType,
          path: databasePath,
        },
      });

      setMessage({ type: "success", text: response.message });

      // Odśwież aktualne info o bazie
      await loadCurrentDatabase();
    } catch (error) {
      setMessage({
        type: "error",
        text: error.response?.data?.detail || "Błąd zapisywania ustawień",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleBrowse = async () => {
    if (!isDesktop) {
      alert("Przeglądanie plików jest dostępne tylko w aplikacji desktopowej");
      return;
    }

    try {
      let result;

      if (databaseType === "network") {
        // Dla sieci - wybór pliku
        result = await settingsAPI.browseDatabaseFile();
      } else {
        // Dla lokalnej - wybór folderu (automatycznie doda app.db)
        result = await settingsAPI.browseDatabaseFolder();
      }

      if (result.path) {
        setDatabasePath(result.path);
        setMessage({
          type: "success",
          text: "Wybrano ścieżkę: " + result.path,
        });
      }
    } catch (error) {
      console.error("Błąd dialogu:", error);
      setMessage({
        type: "error",
        text: "Nie udało się otworzyć dialogu wyboru pliku",
      });
    }
  };

  if (loading) {
    return (
      <div className="settings-page">
        <div className="loading">Ładowanie ustawień...</div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="settings-content">
        {/* Aktualna baza danych */}
        <div className="settings-section">
          <h2>📊 Aktualna baza danych</h2>
          {currentDatabase && (
            <div className="current-db-info">
              <div className="info-row">
                <span className="info-label">Typ:</span>
                <span className="info-value">
                  {currentDatabase.type === "local" ? "Lokalna" : "Sieciowa"}
                </span>
              </div>
              <div className="info-row">
                <span className="info-label">Ścieżka:</span>
                <span className="info-value">{currentDatabase.path}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Status:</span>
                <span
                  className={`info-value ${currentDatabase.exists ? "status-ok" : "status-error"}`}
                >
                  {currentDatabase.exists ? "✓ Dostępna" : "✗ Niedostępna"}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Zmiana bazy danych */}
        <div className="settings-section">
          <h2>🔧 Zmiana bazy danych</h2>
          <p className="section-description">
            Zmiana ustawień wymaga ponownego uruchomienia aplikacji
          </p>

          <div className="form-group">
            <label>Typ bazy danych</label>
            <select
              value={databaseType}
              onChange={(e) => setDatabaseType(e.target.value)}
              className="settings-select"
            >
              <option value="local">Lokalna (na tym komputerze)</option>
              <option value="network">Sieciowa (współdzielona)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Ścieżka do bazy danych</label>
            <div className="path-input-group">
              <input
                type="text"
                value={databasePath}
                onChange={(e) => setDatabasePath(e.target.value)}
                placeholder={
                  databaseType === "network"
                    ? "\\\\serwer\\udział\\app.db"
                    : "C:\\ProgramData\\StrazakApp\\app.db"
                }
                className="settings-input"
              />
              <button onClick={handleBrowse} className="btn-browse">
                📁 Przeglądaj
              </button>
            </div>
            {databaseType === "network" && (
              <p className="input-hint">
                Ścieżka sieciowa musi zaczynać się od \\ (np.
                \\serwer\folder\app.db)
              </p>
            )}
          </div>

          {message && (
            <div className={`message message-${message.type}`}>
              {message.text}
            </div>
          )}

          <div className="form-actions">
            <button onClick={handleSave} disabled={saving} className="btn-save">
              {saving ? "Zapisywanie..." : "💾 Zapisz ustawienia"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
