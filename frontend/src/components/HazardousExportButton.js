import React, { useState } from "react";
import { hazardousRecordsAPI } from "../services/api";
import "./ExportButton.css";

/**
 * HazardousExportButton.js
 * Eksport danych Dodatku Szkodliwego do Excel/CSV.
 * Wzorowany na DeparturesExportButton — identyczna struktura,
 * ale używa hazardousRecordsAPI zamiast dataAPI.
 */
function HazardousExportButton({ fileId, filters = {} }) {
  const [showMenu, setShowMenu] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format) => {
    setExporting(true);
    setShowMenu(false);

    try {
      let response;
      const dateStr = new Date().toISOString().split("T")[0];
      let filename = `dodatek_szkodliwy_${dateStr}`;

      if (format === "excel") {
        response = await hazardousRecordsAPI.exportToExcel(fileId, filters);
        filename = response.filename || `${filename}.xlsx`;
      } else if (format === "csv") {
        response = await hazardousRecordsAPI.exportToCSV(fileId, filters);
        filename = response.filename || `${filename}.csv`;
      }

      const url = window.URL.createObjectURL(response.blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
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

export default HazardousExportButton;
