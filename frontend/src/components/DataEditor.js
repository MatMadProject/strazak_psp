import React, { useState, useEffect } from "react";
import { dataAPI } from "../services/api";
import "./DataEditor.css";

function DataEditor({ record, onClose, onSave }) {
  const [formData, setFormData] = useState({
    nazwa_swd: "",
    kod_swd: "",
    kategoria: "",
    wartosc: "",
    jednostka: "",
    data_pomiaru: "",
    uwagi: "",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (record) {
      setFormData({
        nazwa_swd: record.nazwa_swd || "",
        kod_swd: record.kod_swd || "",
        kategoria: record.kategoria || "",
        wartosc: record.wartosc || "",
        jednostka: record.jednostka || "",
        data_pomiaru: record.data_pomiaru || "",
        uwagi: record.uwagi || "",
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
      // Konwertuj wartość na liczbę
      const updateData = {
        ...formData,
        wartosc: formData.wartosc ? parseFloat(formData.wartosc) : null,
      };

      await dataAPI.updateRecord(record.id, updateData);
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
            <label htmlFor="nazwa_swd">Nazwa SWD</label>
            <input
              type="text"
              id="nazwa_swd"
              name="nazwa_swd"
              value={formData.nazwa_swd}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="kod_swd">Kod SWD</label>
            <input
              type="text"
              id="kod_swd"
              name="kod_swd"
              value={formData.kod_swd}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="kategoria">Kategoria</label>
            <input
              type="text"
              id="kategoria"
              name="kategoria"
              value={formData.kategoria}
              onChange={handleChange}
              className="form-input"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="wartosc">Wartość</label>
              <input
                type="number"
                step="0.01"
                id="wartosc"
                name="wartosc"
                value={formData.wartosc}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="jednostka">Jednostka</label>
              <input
                type="text"
                id="jednostka"
                name="jednostka"
                value={formData.jednostka}
                onChange={handleChange}
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="data_pomiaru">Data pomiaru</label>
            <input
              type="text"
              id="data_pomiaru"
              name="data_pomiaru"
              value={formData.data_pomiaru}
              onChange={handleChange}
              className="form-input"
              placeholder="np. 2024-01-15"
            />
          </div>

          <div className="form-group">
            <label htmlFor="uwagi">Uwagi</label>
            <textarea
              id="uwagi"
              name="uwagi"
              value={formData.uwagi}
              onChange={handleChange}
              className="form-textarea"
              rows="3"
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
