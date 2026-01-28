import React, { useState, useEffect } from "react";
import { dataAPI } from "../services/api";
import "./DataEditor.css";

function DataEditor({ record, isAddingNew, fileId, onClose, onSave }) {
  const [formData, setFormData] = useState({
    nazwisko_imie: "",
    stopien: "",
    funkcja: "",
    nr_meldunku: "",
    czas_rozp_zdarzenia: "",
    p: "",
    mz: "",
    af: "",
    zaliczono_do_emerytury: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (record) {
      setFormData({
        nazwisko_imie: record.nazwisko_imie || "",
        stopien: record.stopien || "",
        funkcja: record.funkcja || "",
        nr_meldunku: record.nr_meldunku || "",
        czas_rozp_zdarzenia: record.czas_rozp_zdarzenia || "",
        p: record.p || "",
        mz: record.mz || "",
        af: record.af || "",
        zaliczono_do_emerytury: record.zaliczono_do_emerytury?.toString() || "", // Konwersja na string
      });
    } else if (isAddingNew) {
      // Reset formularza dla nowego rekordu
      setFormData({
        nazwisko_imie: "",
        stopien: "",
        funkcja: "",
        nr_meldunku: "",
        czas_rozp_zdarzenia: "",
        p: "",
        mz: "",
        af: "",
        zaliczono_do_emerytury: "",
      });
    }
  }, [record, isAddingNew]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Walidacja po stronie frontendu
    if (!formData.nazwisko_imie || !formData.nazwisko_imie.trim()) {
      alert("⚠️ Pole 'Nazwisko i Imię' jest wymagane");
      return;
    }

    if (!formData.nr_meldunku || !formData.nr_meldunku.trim()) {
      alert("⚠️ Pole 'Nr meldunku' jest wymagane");
      return;
    }

    setSaving(true);

    try {
      if (isAddingNew) {
        // Dodawanie nowego rekordu
        await dataAPI.createRecord(fileId, formData);
        alert("✅ Nowy rekord dodany pomyślnie");
      } else {
        // Aktualizacja istniejącego rekordu
        await dataAPI.updateRecord(record.id, formData);
        alert("✅ Rekord zaktualizowany pomyślnie");
      }
      onSave();
    } catch (error) {
      console.error("Błąd zapisu:", error);

      // Obsługa błędu duplikatu
      if (error.response?.status === 409) {
        alert(`⚠️ Duplikat!\n\n${error.response.data.detail}`);
      } else {
        alert(`❌ Błąd: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isAddingNew ? "Dodaj nowe zdarzenie" : "✏️ Edycja rekordu"}</h2>
          <button onClick={onClose} className="btn-close">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="editor-form">
          <div className="form-group">
            <label htmlFor="nazwisko_imie">Nazwisko i Imię *</label>
            <input
              type="text"
              id="nazwisko_imie"
              name="nazwisko_imie"
              value={formData.nazwisko_imie}
              onChange={handleChange}
              className="form-input"
              required
              disabled={!isAddingNew} // Zablokowane przy edycji
              style={
                !isAddingNew
                  ? { backgroundColor: "#f5f5f5", cursor: "not-allowed" }
                  : {}
              }
            />
            {!isAddingNew && (
              <small style={{ color: "#666", fontSize: "0.85em" }}>
                ℹ️ To pole nie może być edytowane
              </small>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="stopien">Stopień</label>
              <input
                type="text"
                id="stopien"
                name="stopien"
                value={formData.stopien}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="funkcja">Funkcja</label>
              <input
                type="text"
                id="funkcja"
                name="funkcja"
                value={formData.funkcja}
                onChange={handleChange}
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="nr_meldunku">Nr meldunku *</label>
            <input
              type="text"
              id="nr_meldunku"
              name="nr_meldunku"
              value={formData.nr_meldunku}
              onChange={handleChange}
              className="form-input"
              required
              disabled={!isAddingNew} // Zablokowane przy edycji
              style={
                !isAddingNew
                  ? { backgroundColor: "#f5f5f5", cursor: "not-allowed" }
                  : {}
              }
            />
            {!isAddingNew && (
              <small style={{ color: "#666", fontSize: "0.85em" }}>
                ℹ️ To pole nie może być edytowane
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="czas_rozp_zdarzenia">
              Czas rozpoczęcia zdarzenia
            </label>
            <input
              type="text"
              id="czas_rozp_zdarzenia"
              name="czas_rozp_zdarzenia"
              value={formData.czas_rozp_zdarzenia}
              onChange={handleChange}
              className="form-input"
              placeholder="np. 2024-08-26 05:04"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="p">P</label>
              <input
                type="text"
                id="p"
                name="p"
                value={formData.p}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="mz">MZ</label>
              <input
                type="text"
                id="mz"
                name="mz"
                value={formData.mz}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="af">AF</label>
              <input
                type="text"
                id="af"
                name="af"
                value={formData.af}
                onChange={handleChange}
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="zaliczono_do_emerytury">
              Zaliczono do emerytury
            </label>
            <select
              id="zaliczono_do_emerytury"
              name="zaliczono_do_emerytury"
              value={formData.zaliczono_do_emerytury}
              onChange={handleChange}
              className="form-input"
            >
              <option value="">Wybierz...</option>
              <option value="1">Tak</option>
              <option value="0">Nie</option>
            </select>
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
                : isAddingNew
                  ? "Dodaj zdarzenie"
                  : "Zapisz zmiany"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DataEditor;
