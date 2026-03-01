import React, { useState, useEffect } from "react";
import Firefighters from "./components/Firefighters";
import Departures from "./components/Departures";
import Settings from "./components/Settings";
import Hazardous from "./components/Hazardous";
import HazardousDegrees from "./components/HazardousDegrees";
import Footer from "./components/Footer";
import { dataAPI, systemAPI } from "./services/api";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("departures");
  const [statistics, setStatistics] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isDesktop, setIsDesktop] = useState(false);
  const [isDev, setIsDev] = useState(false);
  const [hazardousExpanded, setHazardousExpanded] = useState(false);

  useEffect(() => {
    checkEnvironment();
    loadStatistics();
  }, []);

  useEffect(() => {
    if (activeTab === "hazard-degrees" || activeTab === "hazard-addon") {
      setHazardousExpanded(true);
    }
  }, [activeTab]);

  const checkEnvironment = async () => {
    try {
      const data = await systemAPI.getEnvironment();
      setIsDesktop(data.is_desktop);
      console.log("[APP] Environment:", data);
    } catch (error) {
      console.error("[APP] Błąd sprawdzania środowiska:", error);
      setIsDev(window.location.hostname === "localhost");
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await dataAPI.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error("Błąd ładowania statystyk:", error);
    }
  };

  const handleHazardousGroupClick = () => {
    if (sidebarCollapsed) {
      setSidebarCollapsed(false);
      setHazardousExpanded(true);
    } else {
      setHazardousExpanded((prev) => !prev);
    }
  };

  const isHazardousGroupActive =
    activeTab === "hazard-degrees" || activeTab === "hazard-addon";

  const getHeaderTitle = () => {
    switch (activeTab) {
      case "departures":
        return "🚨 Wyjazdy";
      case "firefighters":
        return "👨‍🚒 Strażacy";
      case "settings":
        return "⚙️ Ustawienia";
      case "hazard-degrees":
        return "☣️ Stopnie Szkodliwości";
      case "hazard-addon":
        return "🧪 Dodatek Szkodliwy";
      default:
        return "";
    }
  };

  const getHeaderSubtitle = () => {
    switch (activeTab) {
      case "departures":
        return "Zarządzanie wyjazdami";
      case "firefighters":
        return "Zarządzanie danymi strażaków";
      case "settings":
        return "Konfiguracja aplikacji";
      case "hazard-degrees":
        return "Zarządzanie stopniami szkodliwości";
      case "hazard-addon":
        return "Zarządzanie dodatkami szkodliwymi";
      default:
        return "";
    }
  };

  return (
    <div className="app">
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

          <div
            className={`nav-group ${isHazardousGroupActive ? "group-active" : ""} ${
              hazardousExpanded && !sidebarCollapsed ? "group-expanded" : ""
            }`}
          >
            <button
              className={`nav-item nav-group-header ${isHazardousGroupActive ? "active" : ""}`}
              onClick={handleHazardousGroupClick}
              title="Szkodliwe"
            >
              <span className="nav-icon">☣️</span>
              {!sidebarCollapsed && (
                <>
                  <span className="nav-text">Szkodliwe</span>
                  <span
                    className={`nav-chevron ${hazardousExpanded ? "chevron-open" : ""}`}
                  >
                    ›
                  </span>
                </>
              )}
            </button>

            {hazardousExpanded && !sidebarCollapsed && (
              <div className="nav-subitems">
                <button
                  className={`nav-subitem ${activeTab === "hazard-degrees" ? "active" : ""}`}
                  onClick={() => setActiveTab("hazard-degrees")}
                  title="Stopnie Szkodliwości"
                >
                  <span className="nav-icon nav-icon-sm">📊</span>
                  <span className="nav-text">Stopnie Szkodliwości</span>
                </button>

                <button
                  className={`nav-subitem ${activeTab === "hazard-addon" ? "active" : ""}`}
                  onClick={() => setActiveTab("hazard-addon")}
                  title="Dodatek Szkodliwy"
                >
                  <span className="nav-icon nav-icon-sm">🧪</span>
                  <span className="nav-text">Dodatek Szkodliwy</span>
                </button>
              </div>
            )}
          </div>

          <button
            className={`nav-item ${activeTab === "firefighters" ? "active" : ""}`}
            onClick={() => setActiveTab("firefighters")}
            title="Strażacy"
          >
            <span className="nav-icon">👨‍🚒</span>
            {!sidebarCollapsed && <span className="nav-text">Strażacy</span>}
          </button>

          {(isDesktop || isDev) && (
            <button
              className={`nav-item ${activeTab === "settings" ? "active" : ""}`}
              onClick={() => setActiveTab("settings")}
              title="Ustawienia"
            >
              <span className="nav-icon">⚙️</span>
              {!sidebarCollapsed && (
                <span className="nav-text">Ustawienia</span>
              )}
            </button>
          )}
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

      <div className="main-container">
        <header className="app-header">
          <h1>{getHeaderTitle()}</h1>
          <p>{getHeaderSubtitle()}</p>
        </header>

        <main className="app-main">
          {activeTab === "departures" && <Departures />}
          {activeTab === "hazard-degrees" && <HazardousDegrees />}
          {activeTab === "hazard-addon" && <Hazardous subTab="hazard-addon" />}
          {activeTab === "firefighters" && <Firefighters />}
          {activeTab === "settings" && <Settings isDesktop={isDesktop} />}
        </main>
        <Footer />
      </div>
    </div>
  );
}

export default App;
