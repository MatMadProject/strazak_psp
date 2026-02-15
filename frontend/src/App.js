import React, { useState, useEffect } from "react";
import Firefighters from "./components/Firefighters";
import Departures from "./components/Departures";
import { dataAPI } from "./services/api";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("departures"); // 'departures', 'firefighters'
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

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
        <div className="sidebar-header">
          <div className="app-logo">
            {!sidebarCollapsed && <span className="logo-text">Strażak</span>}
            <button
              className="firetruck-toggle"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              title={sidebarCollapsed ? "Rozwiń menu" : "Zwiń menu"}
            >
              <span className="firetruck-icon">🚒</span>
            </button>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === "departures" ? "active" : ""}`}
            onClick={() => setActiveTab("departures")}
            title="Wyjazdy"
          >
            <span className="nav-icon">🚨</span>
            {!sidebarCollapsed && <span className="nav-text">Wyjazdy</span>}
          </button>

          <button
            className={`nav-item ${activeTab === "firefighters" ? "active" : ""}`}
            onClick={() => setActiveTab("firefighters")}
            title="Strażacy"
          >
            <span className="nav-icon">👨‍🚒</span>
            {!sidebarCollapsed && <span className="nav-text">Strażacy</span>}
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
            {activeTab === "departures" && "🚨 Wyjazdy"}
            {activeTab === "firefighters" && "👨‍🚒 Strażacy"}
          </h1>
        </header>

        <main className="app-main">
          {activeTab === "departures" && (
            <Departures refreshTrigger={refreshTrigger} />
          )}

          {activeTab === "firefighters" && <Firefighters />}
        </main>
      </div>
    </div>
  );
}

export default App;
