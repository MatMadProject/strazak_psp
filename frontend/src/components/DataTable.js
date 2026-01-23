import React, { useState, useEffect } from "react";
import { dataAPI, filesAPI } from "../services/api";
import "./DataTable.css";

function DataTable({ onEditRecord, refreshTrigger }) {
  const [records, setRecords] = useState([]);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(50);

  useEffect(() => {
    loadFiles();
    loadRecords();
  }, [refreshTrigger]);

  useEffect(() => {
    loadRecords();
  }, [selectedFile, searchQuery, currentPage]);

  const loadFiles = async () => {
    try {
      const data = await filesAPI.getAllFiles();
      setFiles(data.files || []);
    } catch (error) {
      console.error("Błąd ładowania plików:", error);
    }
  };

  const loadRecords = async () => {
    setLoading(true);
    console.log(currentPage);
    console.log("records.length", records.length);
    try {
      const params = {
        skip: currentPage * itemsPerPage,
        limit: itemsPerPage,
      };

      if (selectedFile) {
        params.file_id = selectedFile;
      }

      if (searchQuery) {
        params.search = searchQuery;
      }

      const data = await dataAPI.getRecords(params);

      setRecords(data.records || []);
    } catch (error) {
      console.error("Błąd ładowania rekordów:", error);
      alert("Nie udało się załadować danych");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm("Czy na pewno chcesz usunąć ten rekord?")) {
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

  const handleDeleteFile = async (fileId) => {
    if (
      !window.confirm(
        "Czy na pewno chcesz usunąć ten plik i wszystkie jego rekordy?",
      )
    ) {
      return;
    }

    try {
      await filesAPI.deleteFile(fileId);
      loadFiles();
      loadRecords();
    } catch (error) {
      console.error("Błąd usuwania pliku:", error);
      alert("Nie udało się usunąć pliku");
    }
  };

  return (
    <div className="data-table-container">
      <div className="table-header">
        <h2>Dane SWD</h2>

        <div className="table-controls">
          <input
            type="text"
            placeholder="Szukaj..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(0);
            }}
            className="search-input"
          />

          <select
            value={selectedFile || ""}
            onChange={(e) => {
              setSelectedFile(e.target.value ? parseInt(e.target.value) : null);
              setCurrentPage(0);
            }}
            className="file-filter"
          >
            <option value="">Wszystkie pliki</option>
            {files.map((file) => (
              <option key={file.id} value={file.id}>
                {file.filename} ({file.rows_count} rekordów)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Lista plików */}
      {files.length > 0 && (
        <div className="files-list">
          <h3>Zaimportowane pliki ({files.length})</h3>
          <div className="files-grid">
            {files.map((file) => (
              <div key={file.id} className="file-card">
                <div className="file-info">
                  <span className="file-icon">📄</span>
                  <div>
                    <p className="file-name">{file.filename}</p>
                    <p className="file-meta">
                      {new Date(file.imported_at).toLocaleString("pl-PL")} •{" "}
                      {file.rows_count} rekordów
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteFile(file.id)}
                  className="btn-delete-small"
                  title="Usuń plik"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabela rekordów */}
      {loading ? (
        <div className="loading">Ładowanie danych...</div>
      ) : records.length === 0 ? (
        <div className="no-data">
          <p>Brak danych do wyświetlenia</p>
          <p className="hint">Zaimportuj plik Excel aby rozpocząć</p>
        </div>
      ) : (
        <>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Nazwisko i Imię</th>
                  <th>Funkcja</th>
                  <th>Nr meldunku</th>
                  <th>Czas rozpoczęcia</th>
                  <th>P</th>
                  <th>MZ</th>
                  <th>AF</th>
                  <th>Zaliczono do 0.5%</th>
                  <th>Akcje</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr key={record.id}>
                    <td>{record.nazwisko_imie}</td>
                    <td>{record.funkcja}</td>
                    <td>{record.nr_meldunku}</td>
                    <td>{record.czas_rozp_zdarzenia}</td>
                    <td className="numeric">{record.p}</td>
                    <td className="numeric">{record.mz}</td>
                    <td className="numeric">{record.af}</td>
                    <td>{record.zaliczono_do_emerytury}</td>
                    <td className="actions">
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
              onClick={() => setCurrentPage(0)}
              disabled={currentPage === 0}
              className="btn-page"
            >
              Pierwsza ←
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
              disabled={currentPage === 0}
              className="btn-page"
            >
              ← Poprzednia
            </button>
            <span className="page-info">Strona {currentPage + 1}</span>
            <button
              onClick={() => setCurrentPage((p) => p + 1)}
              disabled={records.length < itemsPerPage}
              className="btn-page"
            >
              Następna →
            </button>
            <button
              onClick={() => setCurrentPage(records.length / itemsPerPage)}
              disabled={records.length < itemsPerPage}
              className="btn-page"
            >
              → Ostatnia
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default DataTable;
