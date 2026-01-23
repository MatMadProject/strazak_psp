import React, { useState, useEffect } from "react";
import { firefightersAPI } from "../services/api";
import "./FirefighterEditor.css";

function FirefighterEditor({ firefighter, onClose, onSave }) {
  const [formData, setFormData] = useState({
    nazwisko_imie: "",
    stopien: "",
    stanowisko: "",
    jednostka: "",
  });
  const [saving, setSaving] = useState(false);
  const isNewFirefighter = !firefighter;

  // Predefiniowane opcje
  const stopnieOptions = [
    "Strażak",
    "Starszy strażak",
    "Sekcyjny",
    "Starszy sekcyjny",
    "Młodszy ogniomistrz",
    "Ogniomistrz",
    "Starszy ogniomistrz",
    "Młodszy aspirant",
    "Aspirant",
    "Starszy aspirant",
    "Aspirant sztabowy",
    "Młodszy kapitan",
    "Kapitan",
    "Starszy kapitan",
    "Młodszy brygadier",
    "Brygadier",
    "Starszy brygadier",
    "Nadbrygadier",
    "Generał brygadier",
  ];

  const stanowiskaOptions = [
    "Stażysta",
    "Młodszy ratownik",
    "Ratownik",
    "Starszy ratownik",
    "Młodszy operator sprzętu",
    "Operator sprzętu",
    "Starszy operator sprzętu",
    "Dowódca zastępu",
    "Dowódca sekcji",
    "Zastępca dowódcy zmiany",
    "Dowódca zmiany",
    "Zastępca dowódcy JRG",
    "Dowódca JRG",
  ];

  useEffect(() => {
    if (firefighter) {
      setFormData({
        nazwisko_imie: firefighter.nazwisko_imie || "",
        stopien: firefighter.stopien || "",
        stanowisko: firefighter.stanowisko || "",
        jednostka: firefighter.jednostka || "",
      });
    }
  }, [firefighter]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Walidacja
    if (!formData.nazwisko_imie.trim()) {
      alert("Podaj nazwisko i imię strażaka");
      return;
    }
    if (!formData.stopien.trim()) {
      alert("Wybierz stopień");
      return;
    }
    if (!formData.stanowisko.trim()) {
      alert("Wybierz stanowisko");
      return;
    }
    if (!formData.jednostka.trim()) {
      alert("Podaj jednostkę");
      return;
    }

    setSaving(true);

    try {
      if (isNewFirefighter) {
        await firefightersAPI.createFirefighter(formData);
        alert("Strażak został dodany pomyślnie");
      } else {
        await firefightersAPI.updateFirefighter(firefighter.id, formData);
        alert("Dane strażaka zaktualizowane pomyślnie");
      }
      onSave();
    } catch (error) {
      console.error("Błąd zapisu:", error);
      alert(`Błąd: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content firefighter-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2>
            {isNewFirefighter ? "Dodaj nowego strażaka" : "Edycja strażaka"}
          </h2>
          <button onClick={onClose} className="btn-close">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="editor-form">
          <div className="form-group">
            <label htmlFor="nazwisko_imie">
              Nazwisko i Imię <span className="required">*</span>
            </label>
            <input
              type="text"
              id="nazwisko_imie"
              name="nazwisko_imie"
              value={formData.nazwisko_imie}
              onChange={handleChange}
              className="form-input"
              placeholder="np. KOWALSKI Jan"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="stopien">
                Stopień <span className="required">*</span>
              </label>
              <select
                id="stopien"
                name="stopien"
                value={formData.stopien}
                onChange={handleChange}
                className="form-input"
                required
              >
                <option value="">-- Wybierz stopień --</option>
                {stopnieOptions.map((stopien) => (
                  <option key={stopien} value={stopien}>
                    {stopien}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="stanowisko">
                Stanowisko <span className="required">*</span>
              </label>
              <select
                id="stanowisko"
                name="stanowisko"
                value={formData.stanowisko}
                onChange={handleChange}
                className="form-input"
                required
              >
                <option value="">-- Wybierz stanowisko --</option>
                {stanowiskaOptions.map((stanowisko) => (
                  <option key={stanowisko} value={stanowisko}>
                    {stanowisko}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="jednostka">
              Jednostka <span className="required">*</span>
            </label>
            <input
              type="text"
              id="jednostka"
              name="jednostka"
              value={formData.jednostka}
              onChange={handleChange}
              className="form-input"
              placeholder="np. KP PSP Kraków"
              required
            />
            <small className="form-hint">Podaj pełną nazwę jednostki</small>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={saving}
            >
              Anuluj
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving
                ? "Zapisywanie..."
                : isNewFirefighter
                  ? "✚ Dodaj strażaka"
                  : "💾 Zapisz zmiany"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default FirefighterEditor;
