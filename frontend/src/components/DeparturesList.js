import React, { useState, useEffect } from "react";
import { dataAPI } from "../services/api";
import "./DeparturesList.css";

function DeparturesList({ file, onBack, onEditRecord }) {
  const [records, setRecords] = useState([]);
  const [firefighters, setFirefighters] = useState([]);
  const [selectedFirefighter, setSelectedFirefighter] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(50);

  useEffect(() => {
    loadFirefighters();
    loadRecords();
  }, [file.id, selectedFirefighter, currentPage]);

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

      const data = await dataAPI.getFileRecords(file.id, params);
      setRecords(data.records || []);
    } catch (error) {
      console.error("Błąd ładowania rekordów:", error);
      alert("Nie udało się załadować danych");
    } finally {
      setLoading(false);
    }
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
        <button className="btn-export" onClick={handleExport}>
          📤 Eksportuj do Excel
        </button>
      </div>

      <div className="list-controls">
        <div className="control-group">
          <label htmlFor="firefighter-filter">🔍 Filtruj po strażaku:</label>
          <select
            id="firefighter-filter"
            value={selectedFirefighter}
            onChange={(e) => {
              setSelectedFirefighter(e.target.value);
              setCurrentPage(0);
            }}
            className="firefighter-select"
          >
            <option value="">Wszyscy strażacy ({firefighters.length})</option>
            {firefighters.map((ff) => (
              <option key={ff} value={ff}>
                {ff}
              </option>
            ))}
          </select>
        </div>

        {selectedFirefighter && (
          <button
            className="btn-clear-filter"
            onClick={() => setSelectedFirefighter("")}
          >
            ✕ Wyczyść filtr
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
                  <th>Nazwisko i Imię</th>
                  <th>Stopień</th>
                  <th>Funkcja</th>
                  <th>Nr meldunku</th>
                  <th>Czas rozpoczęcia</th>
                  <th>P</th>
                  <th>MZ</th>
                  <th>AF</th>
                  <th>Zaliczono</th>
                  <th>Akcje</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    <td className="name-cell">{record.nazwisko_imie}</td>
                    <td>{record.stopien}</td>
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
              Strona {currentPage + 1} • Wyświetlono {records.length} rekordów
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
