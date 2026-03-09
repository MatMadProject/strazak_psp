import React, { useState, useEffect } from "react";
import { hazardousRecordsAPI } from "../services/api";
import { hazardousDegreesAPI } from "../services/api";
import "./HazardousRecordEditor.css";

/**
 * HazardousRecordEditor.js
 * Modal edycji / dodawania rekordu Dodatku Szkodliwego.
 * Wzorowany na FirefighterEditor.js — identyczna struktura.
 * CSS izolowany prefiksem hre-
 */
function HazardousRecordEditor({ record, fileId, onClose, onSave }) {
  const isNew = !record;

  const [formData, setFormData] = useState({
    jednostka: "",
    nazwisko_imie: "",
    funkcja: "",
    nr_meldunku: "",
    czas_od: "",
    czas_do: "",
    czas_udzialu: "",
    p: "",
    mz: "",
    af: "",
    dodatek_szkodliwy: "",
    stopien_szkodliwosci: "",
    opis_st_szkodliwosci: "",
    hazardous_degree_id: "",
  });

  const [degrees, setDegrees] = useState([]);
  const [saving, setSaving] = useState(false);

  // ── Załaduj stopnie szkodliwości do dropdownu ─────────────────────────────
  useEffect(() => {
    hazardousDegreesAPI
      .getAll({ limit: 1000 })
      .then((data) => setDegrees(data.records || []))
      .catch((err) => console.error("Błąd ładowania stopni:", err));
  }, []);

  // ── Wypełnij formularz danymi edytowanego rekordu ─────────────────────────
  useEffect(() => {
    if (record) {
      setFormData({
        jednostka: record.jednostka || "",
        nazwisko_imie: record.nazwisko_imie || "",
        funkcja: record.funkcja || "",
        nr_meldunku: record.nr_meldunku || "",
        czas_od: record.czas_od || "",
        czas_do: record.czas_do || "",
        czas_udzialu: record.czas_udzialu || "",
        p: record.p || "",
        mz: record.mz || "",
        af: record.af || "",
        dodatek_szkodliwy: record.dodatek_szkodliwy || "",
        stopien_szkodliwosci: record.stopien_szkodliwosci || "",
        opis_st_szkodliwosci: record.opis_st_szkodliwosci || "",
        hazardous_degree_id: record.hazardous_degree_id || "",
      });
    }
  }, [record]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // ── Zapis ─────────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.nazwisko_imie.trim()) {
      alert("Podaj nazwisko i imię");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        ...formData,
        hazardous_degree_id: formData.hazardous_degree_id
          ? parseInt(formData.hazardous_degree_id)
          : null,
      };

      if (isNew) {
        // Nowy rekord — potrzebujemy file_id
        await hazardousRecordsAPI.createRecord({ ...payload, file_id: fileId });
        alert("Rekord został dodany pomyślnie");
      } else {
        await hazardousRecordsAPI.updateRecord(record.id, payload);
        alert("Rekord zaktualizowany pomyślnie");
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
    <div className="hre-overlay" onClick={onClose}>
      <div className="hre-modal" onClick={(e) => e.stopPropagation()}>
        {/* ─── NAGŁÓWEK ─── */}
        <div className="hre-header">
          <h2>{isNew ? "✚ Dodaj rekord" : "✏️ Edycja rekordu"}</h2>
          <button className="hre-btn-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="hre-form">
          {/* ─── SEKCJA: DANE OSOBY ─── */}
          <div className="hre-section-title">Dane osoby</div>

          <div className="hre-row">
            <div className="hre-group hre-group--wide">
              <label htmlFor="nazwisko_imie">
                Nazwisko i imię <span className="hre-required">*</span>
              </label>
              <input
                type="text"
                id="nazwisko_imie"
                name="nazwisko_imie"
                value={formData.nazwisko_imie}
                onChange={handleChange}
                className="hre-input"
                placeholder="np. KOWALSKI Jan"
                required
              />
            </div>

            <div className="hre-group">
              <label htmlFor="jednostka">Jednostka</label>
              <input
                type="text"
                id="jednostka"
                name="jednostka"
                value={formData.jednostka}
                onChange={handleChange}
                className="hre-input"
                placeholder="np. JRG 1"
              />
            </div>
          </div>

          <div className="hre-row">
            <div className="hre-group">
              <label htmlFor="funkcja">Funkcja</label>
              <input
                type="text"
                id="funkcja"
                name="funkcja"
                value={formData.funkcja}
                onChange={handleChange}
                className="hre-input"
                placeholder="np. Dowódca zastępu"
              />
            </div>

            <div className="hre-group">
              <label htmlFor="nr_meldunku">Nr meldunku</label>
              <input
                type="text"
                id="nr_meldunku"
                name="nr_meldunku"
                value={formData.nr_meldunku}
                onChange={handleChange}
                className="hre-input"
                placeholder="np. 2024/001"
              />
            </div>
          </div>

          {/* ─── SEKCJA: CZAS ─── */}
          <div className="hre-section-title">Czas udziału</div>

          <div className="hre-row">
            <div className="hre-group">
              <label htmlFor="czas_od">Czas od</label>
              <input
                type="text"
                id="czas_od"
                name="czas_od"
                value={formData.czas_od}
                onChange={handleChange}
                className="hre-input"
                placeholder="np. 2024-01-15 08:00"
              />
            </div>

            <div className="hre-group">
              <label htmlFor="czas_do">Czas do</label>
              <input
                type="text"
                id="czas_do"
                name="czas_do"
                value={formData.czas_do}
                onChange={handleChange}
                className="hre-input"
                placeholder="np. 2024-01-15 16:00"
              />
            </div>

            <div className="hre-group hre-group--narrow">
              <label htmlFor="czas_udzialu">Czas udziału</label>
              <input
                type="text"
                id="czas_udzialu"
                name="czas_udzialu"
                value={formData.czas_udzialu}
                onChange={handleChange}
                className="hre-input"
                placeholder="np. 08:00"
              />
            </div>
          </div>

          {/* ─── SEKCJA: FLAGI ─── */}
          <div className="hre-section-title">Flagi</div>

          <div className="hre-row hre-row--flags">
            <div className="hre-group hre-group--narrow">
              <label htmlFor="p">P</label>
              <input
                type="text"
                id="p"
                name="p"
                value={formData.p}
                onChange={handleChange}
                className="hre-input"
                placeholder="—"
              />
            </div>
            <div className="hre-group hre-group--narrow">
              <label htmlFor="mz">MZ</label>
              <input
                type="text"
                id="mz"
                name="mz"
                value={formData.mz}
                onChange={handleChange}
                className="hre-input"
                placeholder="—"
              />
            </div>
            <div className="hre-group hre-group--narrow">
              <label htmlFor="af">AF</label>
              <input
                type="text"
                id="af"
                name="af"
                value={formData.af}
                onChange={handleChange}
                className="hre-input"
                placeholder="—"
              />
            </div>
            <div className="hre-group">
              <label htmlFor="dodatek_szkodliwy">Dodatek szkodliwy</label>
              <input
                type="text"
                id="dodatek_szkodliwy"
                name="dodatek_szkodliwy"
                value={formData.dodatek_szkodliwy}
                onChange={handleChange}
                className="hre-input"
                placeholder="—"
              />
            </div>
          </div>

          {/* ─── SEKCJA: STOPIEŃ SZKODLIWOŚCI ─── */}
          <div className="hre-section-title">Stopień szkodliwości</div>

          <div className="hre-row">
            <div className="hre-group">
              <label htmlFor="stopien_szkodliwosci">
                Stopień szkodliwości (z pliku)
              </label>
              <input
                type="text"
                id="stopien_szkodliwosci"
                name="stopien_szkodliwosci"
                value={formData.stopien_szkodliwosci}
                onChange={handleChange}
                className="hre-input"
                placeholder="—"
              />
            </div>

            <div className="hre-group hre-group--wide">
              <label htmlFor="hazardous_degree_id">
                Przypisany stopień szkodliwości
              </label>
              <select
                id="hazardous_degree_id"
                name="hazardous_degree_id"
                value={formData.hazardous_degree_id}
                onChange={handleChange}
                className={`hre-input hre-select ${formData.hazardous_degree_id ? "hre-select--assigned" : "hre-select--empty"}`}
              >
                <option value="">— brak —</option>
                {degrees.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.stopien}.{d.punkt} — {d.opis}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="hre-group">
            <label htmlFor="opis_st_szkodliwosci">
              Opis stopnia szkodliwości
            </label>
            <textarea
              id="opis_st_szkodliwosci"
              name="opis_st_szkodliwosci"
              value={formData.opis_st_szkodliwosci}
              onChange={handleChange}
              className="hre-input hre-textarea"
              placeholder="Dodatkowy opis..."
              rows={3}
            />
          </div>

          {/* ─── PRZYCISKI ─── */}
          <div className="hre-actions">
            <button
              type="button"
              onClick={onClose}
              className="hre-btn-cancel"
              disabled={saving}
            >
              Anuluj
            </button>
            <button type="submit" className="hre-btn-save" disabled={saving}>
              {saving
                ? "Zapisywanie..."
                : isNew
                  ? "✚ Dodaj rekord"
                  : "💾 Zapisz zmiany"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default HazardousRecordEditor;
