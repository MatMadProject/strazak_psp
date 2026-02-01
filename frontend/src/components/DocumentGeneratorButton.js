import React, { useState } from "react";
import { dataAPI } from "../services/api";
import "./ExportButton.css";

function DocumentGeneratorButton({ fileId, firefighter, filters = {} }) {
  const [showMenu, setShowMenu] = useState(false);
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async (format) => {
    // Walidacja - strażak
    if (!firefighter) {
      alert("⚠️ Musisz wybrać strażaka, aby wygenerować dokument!");
      setShowMenu(false);
      return;
    }

    // Walidacja - daty (obie muszą być wybrane)
    if (!filters.date_from || !filters.date_to) {
      alert("⚠️ Musisz wybrać zakres dat (od - do), aby wygenerować dokument!");
      setShowMenu(false);
      return;
    }

    setGenerating(true);
    setShowMenu(false);

    try {
      const response = await dataAPI.generateDocument(fileId, format, filters);

      // Utwórz link do pobrania
      const url = window.URL.createObjectURL(response.blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = response.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Pokaż komunikat sukcesu
      alert(`✅ Dokument ${response.filename} został wygenerowany pomyślnie!`);
    } catch (error) {
      console.error("Błąd generowania dokumentu:", error);

      if (error.response?.status === 400) {
        alert(`⚠️ ${error.response.data.detail}`);
      } else {
        alert(
          `❌ Błąd generowania dokumentu: ${error.response?.data?.detail || error.message}`,
        );
      }
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="export-button-container">
      <button
        className="btn-create-doc"
        onClick={() => setShowMenu(!showMenu)}
        disabled={generating}
      >
        {generating ? "⏳ Generowanie..." : "📄 Utwórz dokument"}
      </button>

      {showMenu && !generating && (
        <div className="export-menu">
          <button
            className="export-menu-item"
            onClick={() => handleGenerate("docx")}
          >
            <span className="menu-icon">📝</span>
            <span>Word (.docx)</span>
          </button>
          <button
            className="export-menu-item"
            onClick={() => handleGenerate("pdf")}
          >
            <span className="menu-icon">📕</span>
            <span>PDF (.pdf)</span>
          </button>
          <button
            className="export-menu-item"
            onClick={() => handleGenerate("html")}
          >
            <span className="menu-icon">🌐</span>
            <span>HTML (.html)</span>
          </button>
        </div>
      )}

      {showMenu && (
        <div
          className="export-menu-overlay"
          onClick={() => setShowMenu(false)}
        />
      )}
    </div>
  );
}

export default DocumentGeneratorButton;
