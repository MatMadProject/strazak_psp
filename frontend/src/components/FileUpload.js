import React, { useState } from "react";
import { filesAPI } from "../services/api";
import "./FileUpload.css";

/**
 * FileUpload.js
 * Prop `uploadFn` pozwala przekazać dowolną funkcję uploadu.
 * Domyślnie używa filesAPI.uploadFile — zachowanie Departures bez zmian.
 *
 * Użycie dla Hazardous:
 *   <FileUpload
 *     uploadFn={hazardousRecordsAPI.uploadFile}
 *     onUploadSuccess={handleUploadSuccess}
 *     headerText="Import danych: Dodatek Szkodliwy"
 *   />
 */
function FileUpload({ onUploadSuccess, headerText, uploadFn }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  // Domyślnie filesAPI.uploadFile — Departures działa bez zmian
  const doUpload = uploadFn || filesAPI.uploadFile;

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

  const handleUpload = async () => {
    if (!file) {
      alert("Wybierz plik Excel (.xlsx)");
      return;
    }
    setUploading(true);
    try {
      const result = await doUpload(file);
      alert(`Sukces! Zaimportowano ${result.records_imported} rekordów`);
      setFile(null);
      if (onUploadSuccess) onUploadSuccess(result);
    } catch (error) {
      console.error("Błąd uploadu:", error);
      alert(`Błąd: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <h2>{headerText}</h2>

      <div
        className={`drop-zone ${dragActive ? "drag-active" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById("file-input").click()}
      >
        <input
          id="file-input"
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
            <p className="file-types">Akceptowany format: .xlsx</p>
          </div>
        )}
      </div>

      {file && (
        <div className="upload-actions">
          <button
            onClick={() => setFile(null)}
            className="btn-secondary"
            disabled={uploading}
          >
            Anuluj
          </button>
          <button
            onClick={handleUpload}
            className="btn-primary"
            disabled={uploading}
          >
            {uploading ? "Przetwarzanie..." : "Importuj plik"}
          </button>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
