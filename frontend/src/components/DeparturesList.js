import React, { useState, useEffect } from "react";
import { dataAPI } from "../services/api";
import "./DeparturesList.css";

function DeparturesList({ file, onBack, onEditRecord, onAddRecord }) {
  const [records, setRecords] = useState([]);
  const [firefighters, setFirefighters] = useState([]);
  const [selectedFirefighter, setSelectedFirefighter] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(100);
  const [sortBy, setSortBy] = useState("");
  const [sortOrder, setSortOrder] = useState("asc");

  useEffect(() => {
    loadFirefighters();
    loadRecords();
  }, [file.id, selectedFirefighter, currentPage, sortBy, sortOrder]);

  const loadFirefighters = async () => {
    try {
      const data = await dataAPI.getFirefightersInFile(file.id);
      setFirefighters(data.firefighters || []);
    } catch (error) {
      console.error("Błąd ładowania strażaków:", error);
    }
  };

  const loadRecords = async () => {
    setLoading(true);
    try {
      const params = {
        skip: currentPage * itemsPerPage,
        limit: itemsPerPage,
      };

      if (selectedFirefighter) {
        params.firefighter = selectedFirefighter;
      }

      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }

      const data = await dataAPI.getFileRecords(file.id, params);
      setRecords(data.records || []);
    } catch (error) {
      console.error("Błąd ładowania rekordów:", error);
      alert("Nie udało się załadować danych");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (column) => {
    if (sortBy === column) {
      // Zmień kierunek sortowania
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      // Nowa kolumna - sortuj rosnąco
      setSortBy(column);
      setSortOrder("asc");
    }
    setCurrentPage(0);
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm("Czy na pewno chcesz usunąć ten wyjazd?")) {
      return;
    }

    try {
      await dataAPI.deleteRecord(recordId);
      loadRecords();
    } catch (error) {
      console.error("Błąd usuwania rekordu:", error);
      alert("Nie udało się usunąć rekordu");
    }
  };

  const handleExport = () => {
    alert("Eksport do Excel będzie dostępny wkrótce...");
    // TODO: Implementacja eksportu
  };

  const handleCreateDocument = () => {
    alert("Tworzenie dokumentu będzie dostępne wkrótce...");
    // TODO: Implementacja tworzenia dokumentu
  };

  const handleApplyDateFilter = () => {
    // TODO: Implementacja filtrowania po dacie
    alert(
      `Filtrowanie od ${dateFrom || "początku"} do ${dateTo || "końca"} będzie dostępne wkrótce...`,
    );
  };

  const getSortIcon = (column) => {
    if (sortBy !== column) return "↕️";
    return sortOrder === "asc" ? "↑" : "↓";
  };

  return (
    <div className="departures-list-container">
      <div className="list-header">
        <div className="header-left">
          <button className="btn-back" onClick={onBack}>
            ← Powrót
          </button>
          <div className="header-info">
            <h2>📋 Wyjazdy: {file.filename}</h2>
            <p className="file-meta-info">
              📅 {new Date(file.imported_at).toLocaleDateString("pl-PL")} • 📊{" "}
              {file.rows_count} rekordów
            </p>
          </div>
        </div>
        <div className="header-buttons">
          <button className="btn-create-doc" onClick={handleCreateDocument}>
            📄 Utwórz dokument
          </button>
          <button className="btn-export" onClick={handleExport}>
            📤 Eksportuj
          </button>
          <button className="btn-add" onClick={onAddRecord}>
            ✚ Dodaj zdarzenie
          </button>
        </div>
      </div>

      <div className="list-controls">
        <div className="control-group">
          <label htmlFor="firefighter-filter">🔍 Strażak:</label>
          <select
            id="firefighter-filter"
            value={selectedFirefighter}
            onChange={(e) => {
              setSelectedFirefighter(e.target.value);
              setCurrentPage(0);
            }}
            className="firefighter-select"
          >
            <option value="">Wszyscy ({firefighters.length})</option>
            {firefighters.map((ff) => (
              <option key={ff} value={ff}>
                {ff}
              </option>
            ))}
          </select>
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
          <button className="btn-apply-filter" onClick={handleApplyDateFilter}>
            Filtruj
          </button>
        </div>

        {(selectedFirefighter || dateFrom || dateTo) && (
          <button
            className="btn-clear-filter"
            onClick={() => {
              setSelectedFirefighter("");
              setDateFrom("");
              setDateTo("");
            }}
          >
            ✕ Wyczyść filtry
          </button>
        )}
      </div>

      {loading ? (
        <div className="loading">Ładowanie danych...</div>
      ) : records.length === 0 ? (
        <div className="no-data">
          <p>Brak wyjazdów do wyświetlenia</p>
          {selectedFirefighter && (
            <p className="hint">Spróbuj zmienić filtr strażaka</p>
          )}
        </div>
      ) : (
        <>
          <div className="table-wrapper">
            <table className="departures-table">
              <thead>
                <tr>
                  <th
                    onClick={() => handleSort("nazwisko_imie")}
                    className="sortable"
                  >
                    Nazwisko i Imię {getSortIcon("nazwisko_imie")}
                  </th>
                  <th
                    onClick={() => handleSort("funkcja")}
                    className="sortable"
                  >
                    Funkcja {getSortIcon("funkcja")}
                  </th>
                  <th
                    onClick={() => handleSort("nr_meldunku")}
                    className="sortable"
                  >
                    Nr meldunku {getSortIcon("nr_meldunku")}
                  </th>
                  <th
                    onClick={() => handleSort("czas_rozp_zdarzenia")}
                    className="sortable"
                  >
                    Czas rozpoczęcia {getSortIcon("czas_rozp_zdarzenia")}
                  </th>
                  <th
                    onClick={() => handleSort("p")}
                    className="sortable center"
                  >
                    P {getSortIcon("p")}
                  </th>
                  <th
                    onClick={() => handleSort("mz")}
                    className="sortable center"
                  >
                    MZ {getSortIcon("mz")}
                  </th>
                  <th
                    onClick={() => handleSort("af")}
                    className="sortable center"
                  >
                    AF {getSortIcon("af")}
                  </th>
                  <th
                    onClick={() => handleSort("zaliczono_do_emerytury")}
                    className="sortable center"
                  >
                    Zaliczono {getSortIcon("zaliczono_do_emerytury")}
                  </th>
                  <th>Akcje</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    <td className="name-cell">{record.nazwisko_imie}</td>
                    <td>{record.funkcja}</td>
                    <td className="code-cell">{record.nr_meldunku}</td>
                    <td>{record.czas_rozp_zdarzenia}</td>
                    <td className="center-cell">{record.p}</td>
                    <td className="center-cell">{record.mz}</td>
                    <td className="center-cell">{record.af}</td>
                    <td className="center-cell">
                      {record.zaliczono_do_emerytury}
                    </td>
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
              {itemsPerPage} rekordów
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

export default DeparturesList;
