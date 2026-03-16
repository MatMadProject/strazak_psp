import React, { useState } from "react";
import { hazardousRecordsAPI } from "../services/api";
import "./ExportButton.css";

function HazardousDocumentButton({ fileId, firefighter, filters = {} }) {
  const [showMenu, setShowMenu] = useState(false);
  const [generating, setGenerating] = useState(false);

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
      const isDesktop = typeof window.pywebview !== "undefined";
      const firefighterClean = firefighter.replace(/ /g, "_");

      if (format === "html") {
        const blob = await hazardousRecordsAPI.generateDocument(fileId, {
          ...filters,
          format: "html",
        });
        const url = window.URL.createObjectURL(blob);

        if (isDesktop) {
          const link = document.createElement("a");
          link.href = url;
          link.download = `zestawienie_${firefighterClean}.html`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        } else {
          window.open(url, "_blank");
        }
        setTimeout(() => window.URL.revokeObjectURL(url), 2000);
      } else if (format === "docx") {
        const response = await hazardousRecordsAPI.generateDocumentDocx(
          fileId,
          filters,
        );
        const url = window.URL.createObjectURL(response.blob);
        const link = document.createElement("a");
        link.href = url;
        link.download =
          response.filename || `zestawienie_${firefighterClean}.docx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Błąd generowania dokumentu:", error);
      const detail = error.response?.data?.detail || error.message;
      alert(`❌ Błąd generowania dokumentu: ${detail}`);
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
            onClick={() => handleGenerate("html")}
          >
            <span className="menu-icon">🌐</span>
            <span>HTML (.html)</span>
          </button>
          {/* DOCX — będzie dostępne po przygotowaniu szablonu
          <button className="export-menu-item" onClick={() => handleGenerate("docx")}>
            <span className="menu-icon">📝</span>
            <span>Word (.docx)</span>
          </button>
          */}
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

export default HazardousDocumentButton;
