import React, { useState, useEffect } from "react";
import { hazardousDegreesAPI } from "../services/api";
import "./HazardousDegreesEditor.css";

/**
 * HazardousDegreesEditor.js
 * Modal do dodawania / edycji rekordu stopnia szkodliwości.
 * Wzorowany na FirefighterEditor.js — identyczne zachowanie i styl.
 *
 * Props:
 *   record  - rekord do edycji (null = nowy rekord)
 *   onClose - callback zamknięcia bez zapisu
 *   onSave  - callback po pomyślnym zapisie
 */
function HazardousDegreesEditor({ record, onClose, onSave }) {
  const isEditing = Boolean(record);

  const [formData, setFormData] = useState({
    stopien: "",
    punkt: "",
    opis: "",
    uwagi: "",
  });

  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  // Uzupełnij formularz danymi rekordu przy edycji
  useEffect(() => {
    if (record) {
      setFormData({
        stopien: record.stopien ?? "",
        punkt: record.punkt ?? "",
        opis: record.opis ?? "",
        uwagi: record.uwagi ?? "",
      });
    }
  }, [record]);

  // ── Walidacja ─────────────────────────────────────────────────────────────

  const validate = () => {
    const e = {};
    const stopien = parseInt(formData.stopien);
    const punkt = parseInt(formData.punkt);

    if (!formData.stopien || isNaN(stopien) || stopien < 1)
      e.stopien = "Stopień musi być liczbą całkowitą ≥ 1";
    if (!formData.punkt || isNaN(punkt) || punkt < 1)
      e.punkt = "Punkt musi być liczbą całkowitą ≥ 1";
    if (!formData.opis.trim()) e.opis = "Opis jest wymagany";

    setErrors(e);
    return Object.keys(e).length === 0;
  };

  // ── Zapis ─────────────────────────────────────────────────────────────────

  const handleSubmit = async () => {
    if (!validate()) return;
    setSaving(true);
    try {
      const payload = {
        stopien: parseInt(formData.stopien),
        punkt: parseInt(formData.punkt),
        opis: formData.opis.trim(),
        uwagi: formData.uwagi.trim() || null,
      };

      if (isEditing) {
        await hazardousDegreesAPI.update(record.id, payload);
      } else {
        await hazardousDegreesAPI.create(payload);
      }
      onSave();
    } catch (error) {
      console.error("Błąd zapisu:", error);
      alert(`Nie udało się zapisać: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  // Zamknij modal kliknięciem w tło
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="editor-overlay" onClick={handleBackdropClick}>
      <div className="editor-modal">
        <div className="editor-header">
          <h2>
            {isEditing
              ? "✏️ Edytuj stopień szkodliwości"
              : "✚ Dodaj stopień szkodliwości"}
          </h2>
          <button className="editor-close" onClick={onClose} title="Zamknij">
            ✕
          </button>
        </div>

        <div className="editor-body">
          {/* Stopień + Punkt w jednym wierszu */}
          <div className="form-row">
            <div className={`form-group ${errors.stopien ? "has-error" : ""}`}>
              <label>Stopień *</label>
              <input
                type="number"
                min="1"
                value={formData.stopien}
                onChange={(e) => handleChange("stopien", e.target.value)}
                placeholder="np. 1"
                className="form-input"
              />
              {errors.stopien && (
                <span className="field-error">{errors.stopien}</span>
              )}
            </div>

            <div className={`form-group ${errors.punkt ? "has-error" : ""}`}>
              <label>Punkt *</label>
              <input
                type="number"
                min="1"
                value={formData.punkt}
                onChange={(e) => handleChange("punkt", e.target.value)}
                placeholder="np. 1"
                className="form-input"
              />
              {errors.punkt && (
                <span className="field-error">{errors.punkt}</span>
              )}
            </div>

            {/* Podgląd połączonego pola */}
            {formData.stopien && formData.punkt && (
              <div className="form-group form-group-preview">
                <label>Stopień.Punkt</label>
                <div className="preview-badge">
                  {formData.stopien}.{formData.punkt}
                </div>
              </div>
            )}
          </div>

          {/* Opis */}
          <div className={`form-group ${errors.opis ? "has-error" : ""}`}>
            <label>Opis *</label>
            <textarea
              value={formData.opis}
              onChange={(e) => handleChange("opis", e.target.value)}
              placeholder="Opis stopnia szkodliwości..."
              className="form-textarea"
              rows={4}
            />
            {errors.opis && <span className="field-error">{errors.opis}</span>}
          </div>

          {/* Uwagi */}
          <div className="form-group">
            <label>Uwagi</label>
            <textarea
              value={formData.uwagi}
              onChange={(e) => handleChange("uwagi", e.target.value)}
              placeholder="Dodatkowe uwagi (opcjonalnie)..."
              className="form-textarea"
              rows={2}
            />
          </div>
        </div>

        <div className="editor-footer">
          <button className="btn-cancel" onClick={onClose} disabled={saving}>
            Anuluj
          </button>
          <button className="btn-save" onClick={handleSubmit} disabled={saving}>
            {saving
              ? "⏳ Zapisuję..."
              : isEditing
                ? "💾 Zapisz zmiany"
                : "✚ Dodaj rekord"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default HazardousDegreesEditor;
