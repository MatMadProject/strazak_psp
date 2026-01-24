import React, { useState } from "react";
import { firefightersAPI } from "../services/api";
import "./FirefighterFileEditor.css";

function FirefighterFileEditor({ onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [downloadingTemplate, setDownloadingTemplate] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Wybierz plik Excel (.xlsx)");
      return;
    }

    setUploading(true);
    try {
      const result = await firefightersAPI.importFromExcel(file);

      let message = `Sukces! Zaimportowano ${result.created_count} strażaków`;
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

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error("Błąd importu:", error);
      alert(`Błąd: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    setDownloadingTemplate(true);
    try {
      const blob = await firefightersAPI.downloadTemplate();

      // Utwórz link do pobrania
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "szablon_strazacy.xlsx";
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

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content firefighter-file-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2>📥 Import strażaków z pliku Excel</h2>
          <button onClick={onClose} className="btn-close">
            ✕
          </button>
        </div>

        <div className="file-import-content">
          {/* Instrukcje */}
          <div className="import-instructions">
            <h3>📋 Jak zaimportować strażaków?</h3>
            <ol>
              <li>Pobierz pusty szablon Excel</li>
              <li>Wypełnij dane strażaków zgodnie z instrukcją w szablonie</li>
              <li>Zapisz plik</li>
              <li>Wybierz plik poniżej i kliknij "Importuj"</li>
            </ol>
          </div>

          {/* Przycisk pobierania szablonu */}
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
              document.getElementById("file-input-firefighters").click()
            }
          >
            <input
              id="file-input-firefighters"
              type="file"
              accept=".xlsx,.xls"
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
                <p className="file-types">Akceptowane: .xlsx, .xls</p>
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
              {uploading ? "Importowanie..." : "📥 Importuj strażaków"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FirefighterFileEditor;
