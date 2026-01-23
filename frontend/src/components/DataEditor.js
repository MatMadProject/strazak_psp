import React, { useState, useEffect } from "react";
import { dataAPI } from "../services/api";
import "./DataEditor.css";

function DataEditor({ record, onClose, onSave }) {
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
        zaliczono_do_emerytury: record.zaliczono_do_emerytury || "",
      });
    }
  }, [record]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await dataAPI.updateRecord(record.id, formData);
      alert("Rekord zaktualizowany pomyślnie");
      onSave();
    } catch (error) {
      console.error("Błąd aktualizacji:", error);
      alert(`Błąd: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (!record) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edycja rekordu</h2>
          <button onClick={onClose} className="btn-close">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="editor-form">
          <div className="form-group">
            <label htmlFor="nazwisko_imie">Nazwisko i Imię</label>
            <input
              type="text"
              id="nazwisko_imie"
              name="nazwisko_imie"
              value={formData.nazwisko_imie}
              onChange={handleChange}
              className="form-input"
            />
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
            <label htmlFor="nr_meldunku">Nr meldunku</label>
            <input
              type="text"
              id="nr_meldunku"
              name="nr_meldunku"
              value={formData.nr_meldunku}
              onChange={handleChange}
              className="form-input"
            />
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
            <input
              type="text"
              id="zaliczono_do_emerytury"
              name="zaliczono_do_emerytury"
              value={formData.zaliczono_do_emerytury}
              onChange={handleChange}
              className="form-input"
            />
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
              {saving ? "Zapisywanie..." : "Zapisz zmiany"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DataEditor;
