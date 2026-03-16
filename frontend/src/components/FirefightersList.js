import React, { useState, useEffect } from "react";
import { firefightersAPI } from "../services/api";
import "./FirefightersList.css";

function FirefightersList({
  onEditFirefighter,
  refreshTrigger,
  onFiltersChange,
}) {
  const [firefighters, setFirefighters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterUnit, setFilterUnit] = useState("");
  const [filterRank, setFilterRank] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(50);
  const [statistics, setStatistics] = useState(null);

  // Unikalne jednostki i stopnie dla filtrów
  const [units, setUnits] = useState([]);
  const [ranks, setRanks] = useState([]);

  useEffect(() => {
    loadFirefighters();
    loadStatistics();
  }, [refreshTrigger, searchQuery, filterUnit, filterRank, currentPage]);

  // Przekazuj filtry do komponentu rodzica
  useEffect(() => {
    if (onFiltersChange) {
      const filters = {};
      if (searchQuery) filters.search = searchQuery;
      if (filterUnit) filters.jednostka = filterUnit;
      if (filterRank) filters.stopien = filterRank;
      onFiltersChange(filters);
    }
  }, [searchQuery, filterUnit, filterRank, onFiltersChange]);

  const loadFirefighters = async () => {
    setLoading(true);
    try {
      const params = {
        skip: currentPage * itemsPerPage,
        limit: itemsPerPage,
      };

      if (searchQuery) {
        params.search = searchQuery;
      }
      if (filterUnit) {
        params.jednostka = filterUnit;
      }
      if (filterRank) {
        params.stopien = filterRank;
      }

      const data = await firefightersAPI.getAllFirefighters(params);
      setFirefighters(data.firefighters || []);

      // Zbierz unikalne jednostki i stopnie
      const allUnits = [
        ...new Set(data.firefighters.map((ff) => ff.jednostka)),
      ];
      const allRanks = [...new Set(data.firefighters.map((ff) => ff.stopien))];
      setUnits(allUnits);
      setRanks(allRanks);
    } catch (error) {
      console.error("Błąd ładowania strażaków:", error);
      alert("Nie udało się załadować danych strażaków");
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await firefightersAPI.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error("Błąd ładowania statystyk:", error);
    }
  };

  const handleDeleteFirefighter = async (firefighterId, name) => {
    if (!window.confirm(`Czy na pewno chcesz usunąć strażaka: ${name}?`)) {
      return;
    }

    try {
      await firefightersAPI.deleteFirefighter(firefighterId);
      loadFirefighters();
      loadStatistics();
    } catch (error) {
      console.error("Błąd usuwania strażaka:", error);
      alert("Nie udało się usunąć strażaka");
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setFilterUnit("");
    setFilterRank("");
    setCurrentPage(0);
  };

  return (
    <div className="firefighters-container">
      <div className="firefighters-header">
        <h2>Lista strażaków</h2>

        <div className="firefighters-controls">
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
            value={filterUnit}
            onChange={(e) => {
              setFilterUnit(e.target.value);
              setCurrentPage(0);
            }}
            className="filter-select"
          >
            <option value="">Wszystkie jednostki</option>
            {units.map((unit) => (
              <option key={unit} value={unit}>
                {unit}
              </option>
            ))}
          </select>

          <select
            value={filterRank}
            onChange={(e) => {
              setFilterRank(e.target.value);
              setCurrentPage(0);
            }}
            className="filter-select"
          >
            <option value="">Wszystkie stopnie</option>
            {ranks.map((rank) => (
              <option key={rank} value={rank}>
                {rank}
              </option>
            ))}
          </select>

          {(searchQuery || filterUnit || filterRank) && (
            <button onClick={clearFilters} className="btn-clear-filters">
              Wyczyść filtry
            </button>
          )}
        </div>
      </div>

      {/* Tabela/karty */}
      {loading ? (
        <div className="loading">Ładowanie danych...</div>
      ) : firefighters.length === 0 ? (
        <div className="no-data">
          <p>Brak strażaków do wyświetlenia</p>
          <p className="hint">
            Dodaj pierwszego strażaka klikając przycisk powyżej
          </p>
        </div>
      ) : (
        <>
          <div className="firefighters-grid">
            {firefighters.map((firefighter) => (
              <div key={firefighter.id} className="firefighter-card">
                <div className="firefighter-avatar">
                  {firefighter.nazwisko_imie
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .slice(0, 2)}
                </div>
                <div className="firefighter-info">
                  <h3 className="firefighter-name">
                    {firefighter.nazwisko_imie}
                  </h3>
                  <div className="firefighter-details">
                    <div className="detail-item">
                      <span className="detail-icon">⭐</span>
                      <span>{firefighter.stopien}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">💼</span>
                      <span>{firefighter.stanowisko}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">🏢</span>
                      <span>{firefighter.jednostka}</span>
                    </div>
                  </div>
                </div>
                <div className="firefighter-actions">
                  <button
                    onClick={() => onEditFirefighter(firefighter)}
                    className="btn-edit"
                    title="Edytuj"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() =>
                      handleDeleteFirefighter(
                        firefighter.id,
                        firefighter.nazwisko_imie,
                      )
                    }
                    className="btn-delete"
                    title="Usuń"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="pagination">
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
              disabled={firefighters.length < itemsPerPage}
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

export default FirefightersList;
