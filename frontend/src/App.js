import React, { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import DataTable from "./components/DataTable";
import DataEditor from "./components/DataEditor";
import { dataAPI } from "./services/api";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("data"); // 'upload' or 'data'
  const [editingRecord, setEditingRecord] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [statistics, setStatistics] = useState(null);

  useEffect(() => {
    loadStatistics();
  }, [refreshTrigger]);

  const loadStatistics = async () => {
    try {
      const stats = await dataAPI.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error("Błąd ładowania statystyk:", error);
    }
  };

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
    setActiveTab("data");
  };

  const handleEditRecord = (record) => {
    setEditingRecord(record);
  };

  const handleCloseEditor = () => {
    setEditingRecord(null);
  };

  const handleSaveRecord = () => {
    setEditingRecord(null);
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>📊 SWD Desktop App</h1>
          <div className="header-stats">
            {statistics && (
              <>
                <div className="stat-item">
                  <span className="stat-label">Pliki:</span>
                  <span className="stat-value">{statistics.total_files}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Rekordy:</span>
                  <span className="stat-value">{statistics.total_records}</span>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-button ${activeTab === "data" ? "active" : ""}`}
          onClick={() => setActiveTab("data")}
        >
          📋 Dane
        </button>
        <button
          className={`nav-button ${activeTab === "upload" ? "active" : ""}`}
          onClick={() => setActiveTab("upload")}
        >
          ⬆️ Import pliku
        </button>
      </nav>

      <main className="app-main">
        {activeTab === "upload" ? (
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        ) : (
          <DataTable
            onEditRecord={handleEditRecord}
            refreshTrigger={refreshTrigger}
          />
        )}
      </main>

      {editingRecord && (
        <DataEditor
          record={editingRecord}
          onClose={handleCloseEditor}
          onSave={handleSaveRecord}
        />
      )}
    </div>
  );
}

export default App;
