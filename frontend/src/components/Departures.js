import React, { useState, useEffect } from "react";
import { filesAPI } from "../services/api";
import FileUpload from "./FileUpload";
import DeparturesList from "./DeparturesList";
import DataEditor from "./DataEditor";
import "./Departures.css";

function Departures({ refreshTrigger }) {
  // Przywróć ostatni stan z localStorage lub ustaw 'menu'
  const [view, setView] = useState(() => {
    const saved = localStorage.getItem("departures_view");
    return saved || "menu";
  });

  const [files, setFiles] = useState([]);

  const [selectedFile, setSelectedFile] = useState(() => {
    const saved = localStorage.getItem("departures_selectedFile");
    return saved ? JSON.parse(saved) : null;
  });

  const [editingRecord, setEditingRecord] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Zapisz stan do localStorage przy każdej zmianie
  useEffect(() => {
    localStorage.setItem("departures_view", view);
  }, [view]);

  useEffect(() => {
    if (selectedFile) {
      localStorage.setItem(
        "departures_selectedFile",
        JSON.stringify(selectedFile),
      );
    } else {
      localStorage.removeItem("departures_selectedFile");
    }
  }, [selectedFile]);

  useEffect(() => {
    if (view === "file-list") {
      loadFiles();
    }
  }, [view, refreshTrigger]);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const data = await filesAPI.getAllFiles();
      setFiles(data.files || []);
    } catch (error) {
      console.error("Błąd ładowania plików:", error);
      alert("Nie udało się załadować listy plików");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (result) => {
    alert(
      `Sukces! Zaimportowano ${result.records_imported} rekordów z pliku ${result.filename}`,
    );
    setView("menu");
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setView("departures-list");
  };

  const handleBackFromList = () => {
    setSelectedFile(null);
    setView("file-list");
  };

  const handleBackToMenu = () => {
    setSelectedFile(null);
    setView("menu");
    // Opcjonalnie wyczyść localStorage gdy użytkownik wraca do menu
    // localStorage.removeItem('departures_selectedFile');
  };

  const handleEditRecord = (record) => {
    setEditingRecord(record);
  };

  const handleAddRecord = () => {
    setIsAddingNew(true);
  };

  const handleCloseEditor = () => {
    setEditingRecord(null);
    setIsAddingNew(false);
  };

  const handleSaveRecord = () => {
    setEditingRecord(null);
    setIsAddingNew(false);
    setRefreshKey((prev) => prev + 1);
  };

  const handleDeleteFile = async (fileId, filename) => {
    if (
      !window.confirm(
        `Czy na pewno chcesz usunąć plik "${filename}" i wszystkie jego dane?`,
      )
    ) {
      return;
    }

    try {
      await filesAPI.deleteFile(fileId);
      alert("Plik usunięty pomyślnie");
      loadFiles();
    } catch (error) {
      console.error("Błąd usuwania pliku:", error);
      alert("Nie udało się usunąć pliku");
    }
  };

  // Widok menu startowego
  if (view === "menu") {
    return (
      <div className="departures-container">
        <div className="departures-menu">
          <h2>🚨 Zarządzanie wyjazdami</h2>
          <p className="menu-subtitle">Wybierz akcję aby rozpocząć</p>

          <div className="menu-cards">
            <div
              className="menu-card import-card"
              onClick={() => setView("import")}
            >
              <div className="card-icon">📥</div>
              <h3>Import nowego pliku</h3>
              <p>Zaimportuj dane wyjazdów z pliku Excel</p>
              <div className="card-badge">Nowy plik</div>
            </div>

            <div
              className="menu-card open-card"
              onClick={() => setView("file-list")}
            >
              <div className="card-icon">📂</div>
              <h3>Otwórz zaimportowany plik</h3>
              <p>Przeglądaj i edytuj wcześniej zaimportowane dane</p>
              <div className="card-badge">Istniejące pliki</div>
            </div>
          </div>

          <div className="menu-info">
            <div className="info-item">
              <span className="info-icon">ℹ️</span>
              <span>
                Zaimportowane pliki są przechowywane i można do nich wracać
              </span>
            </div>
            <div className="info-item">
              <span className="info-icon">💡</span>
              <span>
                Możesz edytować, filtrować i eksportować dane z każdego pliku
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Widok importu pliku
  if (view === "import") {
    return (
      <div className="departures-container">
        <div className="view-header">
          <button className="btn-back" onClick={handleBackToMenu}>
            ← Powrót
          </button>
          <h2>📥 Import pliku Excel</h2>
        </div>

        <FileUpload
          onUploadSuccess={handleUploadSuccess}
          headerText="Import danych wyjazdów"
        />
      </div>
    );
  }

  // Widok listy plików
  if (view === "file-list") {
    return (
      <div className="departures-container">
        <div className="view-header">
          <button className="btn-back" onClick={handleBackToMenu}>
            ← Powrót
          </button>
          <h2>📂 Zaimportowane pliki</h2>
        </div>

        {loading ? (
          <div className="loading">Ładowanie plików...</div>
        ) : files.length === 0 ? (
          <div className="no-files">
            <div className="no-files-icon">📭</div>
            <h3>Brak zaimportowanych plików</h3>
            <p>Zaimportuj pierwszy plik aby rozpocząć pracę</p>
            <button className="btn-primary" onClick={() => setView("import")}>
              📥 Importuj plik
            </button>
          </div>
        ) : (
          <div className="files-grid">
            {files.map((file) => (
              <div key={file.id} className="file-card">
                <div className="file-card-header">
                  <div className="file-icon-large">📄</div>
                  <div className="file-status" data-status={file.status}>
                    {file.status === "completed" ? "✓" : "⏳"}
                  </div>
                </div>

                <div className="file-card-body">
                  <h3 className="file-title">{file.filename}</h3>

                  <div className="file-meta">
                    <div className="meta-item">
                      <span className="meta-icon">📅</span>
                      <span>
                        {new Date(file.imported_at).toLocaleDateString("pl-PL")}
                      </span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-icon">🕐</span>
                      <span>
                        {new Date(file.imported_at).toLocaleTimeString(
                          "pl-PL",
                          { hour: "2-digit", minute: "2-digit" },
                        )}
                      </span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-icon">📊</span>
                      <span>{file.rows_count} rekordów</span>
                    </div>
                  </div>
                </div>

                <div className="file-card-actions">
                  <button
                    className="btn-open"
                    onClick={() => handleFileSelect(file)}
                  >
                    Otwórz
                  </button>
                  <button
                    className="btn-delete-file"
                    onClick={() => handleDeleteFile(file.id, file.filename)}
                    title="Usuń plik"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Widok listy wyjazdów
  if (view === "departures-list" || view === "departures-list-refresh") {
    return (
      <>
        <DeparturesList
          key={refreshKey}
          file={selectedFile}
          onBack={handleBackFromList}
          onEditRecord={handleEditRecord}
          onAddRecord={handleAddRecord}
        />

        {(editingRecord || isAddingNew) && (
          <DataEditor
            record={editingRecord}
            isAddingNew={isAddingNew}
            fileId={selectedFile?.id}
            onClose={handleCloseEditor}
            onSave={handleSaveRecord}
          />
        )}
      </>
    );
  }

  return null;
}

export default Departures;
