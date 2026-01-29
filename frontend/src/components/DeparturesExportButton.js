import React, { useState } from "react";
import { dataAPI } from "../services/api";
import "./ExportButton.css";

function DeparturesExportButton({ fileId, filters = {} }) {
  const [showMenu, setShowMenu] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format) => {
    setExporting(true);
    setShowMenu(false);

    try {
      let blob;
      let filename;

      if (format === "excel") {
        blob = await dataAPI.exportDeparturesToExcel(fileId, filters);
        filename = blob.filename;
      } else if (format === "csv") {
        blob = await dataAPI.exportDeparturesToCSV(fileId, filters);
        filename = `wyjazdy_${new Date().toISOString().split("T")[0]}.csv`;
      }

      // Utwórz link do pobrania
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Pokaż komunikat sukcesu
      //alert(`✅ Plik ${filename} został pobrany pomyślnie!`);
    } catch (error) {
      console.error("Błąd eksportu:", error);
      alert(
        `❌ Błąd eksportu: ${error.response?.data?.detail || error.message}`,
      );
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="export-button-container">
      <button
        className="btn-export"
        onClick={() => setShowMenu(!showMenu)}
        disabled={exporting}
      >
        {exporting ? "⏳ Eksportowanie..." : "📤 Eksportuj"}
      </button>

      {showMenu && !exporting && (
        <div className="export-menu">
          <button
            className="export-menu-item"
            onClick={() => handleExport("excel")}
          >
            <span className="menu-icon">📊</span>
            <span>Excel (.xlsx)</span>
          </button>
          <button
            className="export-menu-item"
            onClick={() => handleExport("csv")}
          >
            <span className="menu-icon">📄</span>
            <span>CSV (.csv)</span>
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

export default DeparturesExportButton;
