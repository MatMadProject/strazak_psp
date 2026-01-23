import React, { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import DataTable from "./components/DataTable";
import DataEditor from "./components/DataEditor";
import Firefighters from "./components/Firefighters";
import { dataAPI } from "./services/api";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("data"); // 'upload', 'data', 'firefighters'
  const [editingRecord, setEditingRecord] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [statistics, setStatistics] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
        <div className="sidebar-header">
          <div className="app-logo">
            <span className="logo-icon">🚒</span>
            {!sidebarCollapsed && <span className="logo-text">SWD App</span>}
          </div>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? "Rozwiń menu" : "Zwiń menu"}
          >
            {sidebarCollapsed ? "»" : "«"}
          </button>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === "data" ? "active" : ""}`}
            onClick={() => setActiveTab("data")}
            title="Dane SWD"
          >
            <span className="nav-icon">📋</span>
            {!sidebarCollapsed && <span className="nav-text">Dane SWD</span>}
          </button>

          <button
            className={`nav-item ${activeTab === "firefighters" ? "active" : ""}`}
            onClick={() => setActiveTab("firefighters")}
            title="Strażacy"
          >
            <span className="nav-icon">👨‍🚒</span>
            {!sidebarCollapsed && <span className="nav-text">Strażacy</span>}
          </button>

          <button
            className={`nav-item ${activeTab === "upload" ? "active" : ""}`}
            onClick={() => setActiveTab("upload")}
            title="Import pliku"
          >
            <span className="nav-icon">⬆️</span>
            {!sidebarCollapsed && (
              <span className="nav-text">Import pliku</span>
            )}
          </button>
        </nav>

        {!sidebarCollapsed && statistics && (
          <div className="sidebar-stats">
            <div className="stat-box">
              <div className="stat-label">Pliki</div>
              <div className="stat-value">{statistics.total_files}</div>
            </div>
            <div className="stat-box">
              <div className="stat-label">Rekordy</div>
              <div className="stat-value">{statistics.total_records}</div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <div className="main-container">
        <header className="app-header">
          <h1>
            {activeTab === "data" && "📊 Dane SWD"}
            {activeTab === "firefighters" && "👨‍🚒 Strażacy"}
            {activeTab === "upload" && "⬆️ Import pliku"}
          </h1>
        </header>

        <main className="app-main">
          {activeTab === "upload" && (
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          )}

          {activeTab === "data" && (
            <DataTable
              onEditRecord={handleEditRecord}
              refreshTrigger={refreshTrigger}
            />
          )}

          {activeTab === "firefighters" && <Firefighters />}
        </main>
      </div>

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
