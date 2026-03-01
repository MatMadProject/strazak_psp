import React, { useState, useEffect } from "react";
// import { hazardousAPI } from "../services/api";  // podłącz gdy backend gotowy
import "./HazardousList.css";

/**
 * HazardousList.js
 * Komponent listy rekordów dla sekcji "Szkodliwe".
 * Analogiczny do DeparturesList.js.
 *
 * Props:
 *   file         - obiekt pliku { id, filename, imported_at, rows_count }
 *   subTab       - aktywna podzakładka ("hazard-degrees" itp.)
 *   onBack       - callback powrotu do listy plików
 *   onEditRecord - callback otwarcia edytora rekordu
 *   onAddRecord  - callback dodawania nowego rekordu
 */
function HazardousList({ file, subTab, onBack, onEditRecord, onAddRecord }) {
  const [records, setRecords] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(100);
  const [sortBy, setSortBy] = useState("");
  const [sortOrder, setSortOrder] = useState("asc");

  // Filtry - dostosuj do struktury danych Szkodliwych
  const [filterName, setFilterName] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const currentFilters = {
    name: filterName || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  };

  useEffect(() => {
    loadRecords();
  }, [file?.id, filterName, dateFrom, dateTo, currentPage, sortBy, sortOrder]);

  const loadRecords = async () => {
    if (!file?.id) return;
    setLoading(true);
    try {
      // TODO: Zastąp wywołaniem właściwego API
      // const params = {
      //   skip: currentPage * itemsPerPage,
      //   limit: itemsPerPage,
      //   ...(filterName && { name: filterName }),
      //   ...(dateFrom && { date_from: dateFrom }),
      //   ...(dateTo && { date_to: dateTo }),
      //   ...(sortBy && { sort_by: sortBy, sort_order: sortOrder }),
      // };
      // const data = await hazardousAPI.getFileRecords(file.id, params);
      // setRecords(data.records || []);
      // setTotalCount(data.total_count || 0);

      // Tymczasowo puste dane - backend do podłączenia
      setRecords([]);
      setTotalCount(0);
    } catch (error) {
      console.error("Błąd ładowania rekordów:", error);
      alert("Nie udało się załadować danych");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
    setCurrentPage(0);
  };

  const getSortIcon = (column) => {
    if (sortBy !== column) return "↕️";
    return sortOrder === "asc" ? "↑" : "↓";
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm("Czy na pewno chcesz usunąć ten rekord?")) return;
    try {
      // TODO: await hazardousAPI.deleteRecord(recordId);
      loadRecords();
    } catch (error) {
      console.error("Błąd usuwania rekordu:", error);
      alert("Nie udało się usunąć rekordu");
    }
  };

  const hasActiveFilters = filterName || dateFrom || dateTo;

  return (
    <div className="hazardous-list-container">
      {/* ─── NAGŁÓWEK ─── */}
      <div className="list-header">
        <div className="header-left">
          <button className="btn-back" onClick={onBack}>
            ← Powrót
          </button>
          <div className="header-info">
            <h2>☣️ Stopnie Szkodliwości: {file?.filename}</h2>
            <p className="file-meta-info">
              📅 {new Date(file?.imported_at).toLocaleDateString("pl-PL")} • 📊{" "}
              {file?.rows_count} rekordów
            </p>
          </div>
        </div>

        <div className="header-buttons">
          {/* Utwórz dokument */}
          <button
            className="btn-create-doc"
            onClick={() => {
              // TODO: podłączyć DocumentGeneratorButton dla Szkodliwych
              alert("Generowanie dokumentu — do podłączenia z backendem");
            }}
            title="Utwórz dokument"
          >
            📄 Utwórz dokument
          </button>

          {/* Eksport */}
          <button
            className="btn-export"
            onClick={() => {
              // TODO: podłączyć ExportButton dla Szkodliwych
              alert("Eksport — do podłączenia z backendem");
            }}
            title="Eksportuj do Excel"
          >
            📊 Eksportuj
          </button>

          {/* Dodaj zdarzenie */}
          <button className="btn-add" onClick={onAddRecord}>
            ✚ Dodaj zdarzenie
          </button>
        </div>
      </div>

      {/* ─── FILTRY ─── */}
      <div className="list-controls">
        <div className="control-group">
          <label htmlFor="hazardous-name-filter">🔍 Nazwa:</label>
          <input
            id="hazardous-name-filter"
            type="text"
            value={filterName}
            onChange={(e) => {
              setFilterName(e.target.value);
              setCurrentPage(0);
            }}
            placeholder="Szukaj..."
            className="filter-input"
          />
        </div>

        <div className="control-group date-filter">
          <label>📅 Data od:</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="date-input"
          />
          <label>do:</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="date-input"
          />
        </div>

        {hasActiveFilters && (
          <button
            className="btn-clear-filter"
            onClick={() => {
              setFilterName("");
              setDateFrom("");
              setDateTo("");
              setCurrentPage(0);
            }}
          >
            ✕ Wyczyść filtry
          </button>
        )}
      </div>

      {/* ─── TABELA / STANY ─── */}
      {loading ? (
        <div className="loading">Ładowanie danych...</div>
      ) : records.length === 0 ? (
        <div className="no-data">
          <div className="no-data-icon">📭</div>
          <p>Brak rekordów do wyświetlenia</p>
          {hasActiveFilters && (
            <p className="hint">Spróbuj zmienić lub wyczyścić filtry</p>
          )}
          {!hasActiveFilters && (
            <p className="hint">Dodaj pierwsze zdarzenie lub podłącz backend</p>
          )}
        </div>
      ) : (
        <>
          <div className="table-wrapper">
            <table className="hazardous-table">
              <thead>
                <tr>
                  {/* TODO: Dostosuj kolumny do struktury danych Szkodliwych */}
                  <th
                    onClick={() => handleSort("nazwisko_imie")}
                    className="sortable"
                  >
                    Nazwisko i Imię {getSortIcon("nazwisko_imie")}
                  </th>
                  <th
                    onClick={() => handleSort("stopien")}
                    className="sortable"
                  >
                    Stopień Szkodliwości {getSortIcon("stopien")}
                  </th>
                  <th onClick={() => handleSort("data")} className="sortable">
                    Data {getSortIcon("data")}
                  </th>
                  <th
                    onClick={() => handleSort("kategoria")}
                    className="sortable"
                  >
                    Kategoria {getSortIcon("kategoria")}
                  </th>
                  <th>Akcje</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    {/* TODO: Dopasuj pola do modelu danych */}
                    <td className="name-cell">{record.nazwisko_imie}</td>
                    <td>{record.stopien}</td>
                    <td>{record.data}</td>
                    <td>{record.kategoria}</td>
                    <td className="actions-cell">
                      <button
                        onClick={() => onEditRecord(record)}
                        className="btn-edit"
                        title="Edytuj"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDeleteRecord(record.id)}
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
              Strona {currentPage + 1} • Wyświetlono {records.length} z{" "}
              {totalCount} rekordów
              {hasActiveFilters && (
                <span style={{ fontSize: "0.9em", color: "#666" }}>
                  {" "}
                  (filtrowane)
                </span>
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

export default HazardousList;
