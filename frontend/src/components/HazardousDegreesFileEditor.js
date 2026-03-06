import React, { useState } from "react";
import { hazardousDegreesAPI } from "../services/api";
import "./HazardousDegreesFileEditor.css";

/**
 * HazardousDegreesFileEditor.js
 * Modal importu stopni szkodliwości z pliku Excel.
 * Wzorowany 1:1 na FirefighterFileEditor.js — identyczna struktura i zachowanie.
 */
function HazardousDegreesFileEditor({ onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [downloadingTemplate, setDownloadingTemplate] = useState(false);

  // ── Obsługa pliku ─────────────────────────────────────────────────────────

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) setFile(selectedFile);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  // ── Import ────────────────────────────────────────────────────────────────

  const handleUpload = async () => {
    if (!file) {
      alert("Wybierz plik Excel (.xlsx)");
      return;
    }

    setUploading(true);
    try {
      const result = await hazardousDegreesAPI.importFromExcel(file);

      let message = `Sukces! Zaimportowano ${result.created_count} rekordów`;
      if (result.skipped_count > 0) {
        message += `\n\nPominięto ${result.skipped_count} rekordów`;
        if (result.errors && result.errors.length > 0) {
          message += `\n\nBłędy:\n${result.errors.slice(0, 5).join("\n")}`;
          if (result.errors.length > 5) {
            message += `\n... i ${result.errors.length - 5} więcej`;
          }
        }
      }

      alert(message);
      setFile(null);
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error("Błąd importu:", error);
      alert(`Błąd: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  // ── Pobieranie szablonu ───────────────────────────────────────────────────

  const handleDownloadTemplate = async () => {
    setDownloadingTemplate(true);
    try {
      const blob = await hazardousDegreesAPI.downloadTemplate();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "szablon_stopnie_szkodliwosci.xlsx";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Błąd pobierania szablonu:", error);
      alert("Nie udało się pobrać szablonu");
    } finally {
      setDownloadingTemplate(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content hazardous-file-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2>📥 Import stopni szkodliwości z pliku Excel</h2>
          <button onClick={onClose} className="btn-close">
            ✕
          </button>
        </div>

        <div className="file-import-content">
          {/* Instrukcje */}
          <div className="import-instructions">
            <h3>📋 Jak zaimportować stopnie szkodliwości?</h3>
            <ol>
              <li>Pobierz pusty szablon Excel</li>
              <li>
                Wypełnij dane — kolumny: <strong>Stopień</strong>,{" "}
                <strong>Punkt</strong>, <strong>Opis</strong>, <em>Uwagi</em>{" "}
                (opcjonalne)
              </li>
              <li>
                Stopień i Punkt muszą być liczbami całkowitymi (np. 1, 2, 3)
              </li>
              <li>Zapisz plik i wybierz go poniżej</li>
            </ol>
          </div>

          {/* Pobieranie szablonu */}
          <div className="template-download-section">
            <button
              onClick={handleDownloadTemplate}
              className="btn-download-template"
              disabled={downloadingTemplate}
            >
              {downloadingTemplate
                ? "Pobieranie..."
                : "📄 Pobierz pusty szablon Excel"}
            </button>
          </div>

          {/* Drop zone */}
          <div
            className={`drop-zone ${dragActive ? "drag-active" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() =>
              document.getElementById("file-input-hazardous").click()
            }
          >
            <input
              id="file-input-hazardous"
              type="file"
              accept=".xlsx"
              onChange={handleFileChange}
              style={{ display: "none" }}
            />

            {file ? (
              <div className="file-selected">
                <span className="file-icon">📄</span>
                <p className="file-name">{file.name}</p>
                <p className="file-size">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div className="drop-zone-content">
                <span className="upload-icon">⬆️</span>
                <p>Przeciągnij plik Excel tutaj</p>
                <p className="drop-zone-hint">lub kliknij aby wybrać plik</p>
                <p className="file-types">Akceptowane: .xlsx</p>
              </div>
            )}
          </div>

          {/* Przyciski akcji */}
          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={uploading}
            >
              Anuluj
            </button>

            {file && (
              <button
                onClick={() => setFile(null)}
                className="btn-clear"
                disabled={uploading}
              >
                Wyczyść
              </button>
            )}

            <button
              onClick={handleUpload}
              className="btn-primary"
              disabled={uploading || !file}
            >
              {uploading ? "Importowanie..." : "📥 Importuj stopnie"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HazardousDegreesFileEditor;
