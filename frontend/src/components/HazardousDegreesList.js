import React, { useState, useEffect, useCallback } from "react";
import { hazardousDegreesAPI } from "../services/api";
import "./HazardousDegreesList.css";

// ─── Helpers: konwersja cyfr arabskich ────────────────────────────────────────

const ROMAN = [
  [1000, "M"],
  [900, "CM"],
  [500, "D"],
  [400, "CD"],
  [100, "C"],
  [90, "XC"],
  [50, "L"],
  [40, "XL"],
  [10, "X"],
  [9, "IX"],
  [5, "V"],
  [4, "IV"],
  [1, "I"],
];

function toRoman(n) {
  if (!n || n < 1) return String(n);
  let result = "";
  for (const [value, numeral] of ROMAN) {
    while (n >= value) {
      result += numeral;
      n -= value;
    }
  }
  return result;
}

const WORDS_ONES = [
  "",
  "pierwszy",
  "drugi",
  "trzeci",
  "czwarty",
  "piąty",
  "szósty",
  "siódmy",
  "ósmy",
  "dziewiąty",
  "dziesiąty",
  "jedenasty",
  "dwunasty",
  "trzynasty",
  "czternasty",
  "piętnasty",
  "szesnasty",
  "siedemnasty",
  "osiemnasty",
  "dziewiętnasty",
];
const WORDS_TENS = [
  "",
  "",
  "dwudziesty",
  "trzydziesty",
  "czterdziesty",
  "pięćdziesiąty",
];

function toWords(n) {
  if (!n || n < 1) return String(n);
  if (n < 20) return WORDS_ONES[n];
  const tens = Math.floor(n / 10);
  const ones = n % 10;
  return ones === 0
    ? WORDS_TENS[tens]
    : `${WORDS_TENS[tens]} ${WORDS_ONES[ones]}`;
}

function formatNumber(n, format) {
  switch (format) {
    case "roman":
      return toRoman(n);
    case "words":
      return toWords(n);
    default:
      return String(n);
  }
}

// ─── Komponent ────────────────────────────────────────────────────────────────

function HazardousDegreesList({
  onEditRecord,
  refreshTrigger,
  onFiltersChange,
  onAddNew,
  onImportClick,
}) {
  const [records, setRecords] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);

  // Filtry
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStopien, setFilterStopien] = useState("");

  // Format wyświetlania cyfr: arabic | roman | words
  const [numFormat, setNumFormat] = useState("arabic");

  // Widok: cards | list
  const [viewMode, setViewMode] = useState("list");

  // Paginacja
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(50);

  // Unikalne stopnie dla filtra selecta
  const [stopienOptions, setStopienOptions] = useState([]);

  // Eksport dropdown
  const [exportOpen, setExportOpen] = useState(false);

  // ── Ładowanie danych ──────────────────────────────────────────────────────

  const buildParams = useCallback(() => {
    const params = { skip: currentPage * itemsPerPage, limit: itemsPerPage };
    if (searchQuery) params.search = searchQuery;
    if (filterStopien) params.stopien = filterStopien;
    return params;
  }, [currentPage, itemsPerPage, searchQuery, filterStopien]);

  const loadRecords = useCallback(async () => {
    setLoading(true);
    try {
      const data = await hazardousDegreesAPI.getAll(buildParams());
      setRecords(data.records || []);
      setTotalCount(data.total_count || 0);

      // Zbierz unikalne stopnie z bieżącej strony
      const unique = [
        ...new Set((data.records || []).map((r) => r.stopien)),
      ].sort((a, b) => a - b);
      setStopienOptions((prev) =>
        [...new Set([...prev, ...unique])].sort((a, b) => a - b),
      );
    } catch (error) {
      console.error("Błąd ładowania stopni szkodliwości:", error);
      alert("Nie udało się załadować danych");
    } finally {
      setLoading(false);
    }
  }, [buildParams]);

  const loadStopienOptions = useCallback(async () => {
    // Pobierz statystyki tylko dla uzupełnienia opcji filtra — nie renderujemy ich
    try {
      const stats = await hazardousDegreesAPI.getStatistics();
      const fromStats = (stats.by_degree || [])
        .map((d) => d.stopien)
        .sort((a, b) => a - b);
      setStopienOptions(fromStats);
    } catch (error) {
      console.error("Błąd ładowania opcji stopni:", error);
    }
  }, []);

  useEffect(() => {
    loadRecords();
  }, [refreshTrigger, searchQuery, filterStopien, currentPage]);

  useEffect(() => {
    loadStopienOptions();
  }, [refreshTrigger]);

  // Przekaż aktywne filtry do rodzica
  useEffect(() => {
    if (onFiltersChange) {
      const filters = {};
      if (searchQuery) filters.search = searchQuery;
      if (filterStopien) filters.stopien = filterStopien;
      onFiltersChange(filters);
    }
  }, [searchQuery, filterStopien, onFiltersChange]);

  // ── Akcje ─────────────────────────────────────────────────────────────────

  const handleDelete = async (record) => {
    const label = `${formatNumber(record.stopien, numFormat)}.${formatNumber(record.punkt, numFormat)}`;
    if (!window.confirm(`Czy na pewno chcesz usunąć rekord ${label}?`)) return;
    try {
      await hazardousDegreesAPI.delete(record.id);
      loadRecords();
      loadStopienOptions();
    } catch (error) {
      console.error("Błąd usuwania:", error);
      alert("Nie udało się usunąć rekordu");
    }
  };

  // Helper: blob → tymczasowy link download (wzorzec z exportDeparturesToExcel)
  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleExportExcel = async () => {
    setExportOpen(false);
    try {
      const blob = await hazardousDegreesAPI.exportToExcel(currentFilters);
      downloadBlob(
        blob,
        `stopnie_szkodliwosci_${new Date().toISOString().split("T")[0]}.xlsx`,
      );
    } catch (error) {
      console.error("Błąd eksportu XLSX:", error);
      alert("Nie udało się wyeksportować danych");
    }
  };

  const handleExportCsv = async () => {
    setExportOpen(false);
    try {
      const blob = await hazardousDegreesAPI.exportToCSV(currentFilters);
      downloadBlob(
        blob,
        `stopnie_szkodliwosci_${new Date().toISOString().split("T")[0]}.csv`,
      );
    } catch (error) {
      console.error("Błąd eksportu CSV:", error);
      alert("Nie udało się wyeksportować danych");
    }
  };

  const handleDownloadTemplate = async () => {
    setExportOpen(false);
    try {
      const blob = await hazardousDegreesAPI.downloadTemplate();
      downloadBlob(blob, "szablon_stopnie_szkodliwosci.xlsx");
    } catch (error) {
      console.error("Błąd pobierania szablonu:", error);
      alert("Nie udało się pobrać szablonu");
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setFilterStopien("");
    setCurrentPage(0);
  };

  const currentFilters = {
    search: searchQuery || undefined,
    stopien: filterStopien || undefined,
  };

  const hasActiveFilters = searchQuery || filterStopien;

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="hazardous-degrees-container">
      {/* ─── TOOLBAR ─── */}
      <div className="degrees-toolbar">
        <div className="degrees-toolbar-left">
          <h2>Lista stopni szkodliwości</h2>
        </div>

        <div className="degrees-toolbar-right">
          {/* Format liczb */}
          {/* FORMAT SWITCHER — zakomentowane, logika numFormat zachowana na później
          <div className="format-switcher">
            <span className="format-label">Format:</span>
            {[
              { key: "arabic", label: "1, 2, 3"   },
              { key: "roman",  label: "I, II, III" },
              { key: "words",  label: "słownie"    },
            ].map(f => (
              <button
                key={f.key}
                className={`format-btn ${numFormat === f.key ? "active" : ""}`}
                onClick={() => setNumFormat(f.key)}
                title={f.label}
              >
                {f.label}
              </button>
            ))}
          </div>
          */}

          {/* Toggle widoku: kafelki / lista */}
          <div className="view-switcher">
            <button
              className={`view-btn ${viewMode === "cards" ? "active" : ""}`}
              onClick={() => setViewMode("cards")}
              title="Widok kafelków"
            >
              ⊞
            </button>
            <button
              className={`view-btn ${viewMode === "list" ? "active" : ""}`}
              onClick={() => setViewMode("list")}
              title="Widok listy"
            >
              ☰
            </button>
          </div>
          {/* Eksport dropdown */}
          <div className="export-dropdown-wrapper">
            <button
              className="btn-export-toggle"
              onClick={() => setExportOpen((o) => !o)}
            >
              📊 Eksportuj ▾
            </button>
            {exportOpen && (
              <div className="export-dropdown">
                <button onClick={handleExportExcel}>📗 Eksport XLSX</button>
                <button onClick={handleExportCsv}>📄 Eksport CSV</button>
                {/* <hr />
                <button onClick={handleDownloadTemplate}>
                  📥 Pobierz szablon
                </button> */}
              </div>
            )}
          </div>
          <div className="degrees-toolbar-actions">
            {onImportClick && (
              <button onClick={onImportClick} className="btn-import">
                📥 Import z Excel
              </button>
            )}
            {onAddNew && (
              <button onClick={onAddNew} className="btn-add-new">
                ✚ Dodaj stopień
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ─── FILTRY ─── */}
      <div className="degrees-controls">
        <div className="control-group">
          <label>🔍 Szukaj:</label>
          <input
            type="text"
            placeholder="Szukaj w opisie lub uwagach..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(0);
            }}
            className="search-input"
          />
        </div>

        <div className="control-group">
          <label>📊 Stopień:</label>
          <select
            value={filterStopien}
            onChange={(e) => {
              setFilterStopien(e.target.value);
              setCurrentPage(0);
            }}
            className="filter-select"
          >
            <option value="">Wszystkie stopnie</option>
            {stopienOptions.map((s) => (
              <option key={s} value={s}>
                {s} — {toRoman(s)} — {toWords(s)}
              </option>
            ))}
          </select>
        </div>

        {hasActiveFilters && (
          <button className="btn-clear-filters" onClick={clearFilters}>
            ✕ Wyczyść filtry
          </button>
        )}
      </div>

      {/* ─── DANE / STANY ─── */}
      {loading ? (
        <div className="loading">Ładowanie danych...</div>
      ) : records.length === 0 ? (
        <div className="no-data">
          <div className="no-data-icon">📭</div>
          <p>Brak rekordów do wyświetlenia</p>
          <p className="hint">
            {hasActiveFilters
              ? "Spróbuj zmienić lub wyczyścić filtry"
              : "Dodaj pierwszy rekord lub zaimportuj plik xlsx"}
          </p>
        </div>
      ) : (
        <>
          {/* ══ WIDOK KAFELKÓW ══ */}
          {viewMode === "cards" && (
            <div className="degrees-grid">
              {records.map((record) => (
                <div key={record.id} className="degree-card">
                  <div className="degree-avatar">
                    <span className="avatar-arabic">
                      {record.stopien}.{record.punkt}
                    </span>
                    {numFormat !== "arabic" && (
                      <span className="avatar-secondary">
                        {formatNumber(record.stopien, numFormat)}.
                        {formatNumber(record.punkt, numFormat)}
                      </span>
                    )}
                  </div>

                  <div className="degree-info">
                    <div className="degree-header-row">
                      <span className="degree-badge">
                        Stopień {formatNumber(record.stopien, numFormat)}
                        {" · "}
                        Punkt {formatNumber(record.punkt, numFormat)}
                      </span>
                    </div>
                    <p className="degree-opis">{record.opis}</p>
                    {record.uwagi && (
                      <p className="degree-uwagi">
                        <span className="uwagi-label">Uwagi:</span>{" "}
                        {record.uwagi}
                      </p>
                    )}
                  </div>

                  <div className="degree-actions">
                    <button
                      onClick={() => onEditRecord(record)}
                      className="btn-edit"
                      title="Edytuj"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={() => handleDelete(record)}
                      className="btn-delete"
                      title="Usuń"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ══ WIDOK LISTY ══ */}
          {viewMode === "list" && (
            <div className="table-wrapper">
              <table className="degrees-table">
                <thead>
                  <tr>
                    <th>Stopień</th>
                    <th>Punkt</th>
                    <th>Stopień.Punkt</th>
                    <th>Opis</th>
                    <th>Uwagi</th>
                    <th>Akcje</th>
                  </tr>
                </thead>
                <tbody>
                  {records.map((record) => (
                    <tr key={record.id}>
                      <td className="center-cell">
                        <span
                          title={`${toRoman(record.stopien)} — ${toWords(record.stopien)}`}
                        >
                          {formatNumber(record.stopien, numFormat)}
                        </span>
                      </td>
                      <td className="center-cell">
                        <span
                          title={`${toRoman(record.punkt)} — ${toWords(record.punkt)}`}
                        >
                          {formatNumber(record.punkt, numFormat)}
                        </span>
                      </td>
                      <td className="center-cell code-cell">
                        {formatNumber(record.stopien, numFormat)}.
                        {formatNumber(record.punkt, numFormat)}
                      </td>
                      <td className="opis-cell">{record.opis}</td>
                      <td className="uwagi-cell">{record.uwagi || "—"}</td>
                      <td className="actions-cell">
                        <button
                          onClick={() => onEditRecord(record)}
                          className="btn-edit"
                          title="Edytuj"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => handleDelete(record)}
                          className="btn-delete"
                          title="Usuń"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* ─── PAGINACJA ─── */}
          <div className="pagination">
            <button
              onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
              disabled={currentPage === 0}
              className="btn-page"
            >
              ← Poprzednia
            </button>
            <span className="page-info">
              Strona {currentPage + 1} · Wyświetlono {records.length} z{" "}
              {totalCount} rekordów
              {hasActiveFilters && (
                <span className="filter-note"> (filtrowane)</span>
              )}
            </span>
            <button
              onClick={() => setCurrentPage((p) => p + 1)}
              disabled={records.length < itemsPerPage}
              className="btn-page"
            >
              Następna →
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default HazardousDegreesList;
