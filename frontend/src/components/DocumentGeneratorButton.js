import React, { useState } from "react";
import { dataAPI } from "../services/api";
import "./ExportButton.css";

function DocumentGeneratorButton({
  fileId,
  firefighter,
  filters = {},
  disabled = false,
  disabledTooltip = "",
}) {
  const [showMenu, setShowMenu] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Jeśli przycisk wyłączony — pokaż tooltip zamiast menu
  const handleClick = () => {
    if (disabled) {
      alert(disabledTooltip || "Funkcja niedostępna");
      return;
    }
    setShowMenu(!showMenu);
  };

  const handleGenerate = async (format) => {
    if (!firefighter) {
      alert("⚠️ Musisz wybrać strażaka, aby wygenerować dokument!");
      setShowMenu(false);
      return;
    }

    if (!filters.date_from || !filters.date_to) {
      alert("⚠️ Musisz wybrać zakres dat (od - do), aby wygenerować dokument!");
      setShowMenu(false);
      return;
    }

    setGenerating(true);
    setShowMenu(false);

    try {
      const response = await dataAPI.generateDocument(fileId, format, filters);

      const isDesktop = typeof window.pywebview !== "undefined";

      if (format === "html" && !isDesktop) {
        const url = window.URL.createObjectURL(response.blob);
        window.open(url, "_blank");
        setTimeout(() => window.URL.revokeObjectURL(url), 1000);
      } else {
        const url = window.URL.createObjectURL(response.blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = response.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
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
        onClick={handleClick}
        disabled={generating}
        title={disabled ? disabledTooltip : ""}
        style={disabled ? { opacity: 0.5, cursor: "not-allowed" } : {}}
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
