import React, { useState, useEffect } from "react";
// import { hazardousDegreesAPI } from "../services/api"; // podłącz gdy backend gotowy
import "./HazardousDegreesList.css";

/**
 * HazardousDegreesList.js
 * Lista stopni szkodliwości w formie kart.
 * Wzorowany na FirefightersList.js — statystyki, filtry, grid kart, paginacja.
 *
 * Props:
 *   onEditRecord    - callback otwarcia edytora
 *   refreshTrigger  - licznik do wymuszania odświeżenia
 *   onFiltersChange - callback przekazujący aktywne filtry do rodzica
 */
function HazardousDegreesList({
  onEditRecord,
  refreshTrigger,
  onFiltersChange,
}) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterDegree, setFilterDegree] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(50);
  const [statistics, setStatistics] = useState(null);

  // Unikalne wartości dla filtrów - uzupełniane z danych
  const [degrees, setDegrees] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadRecords();
    loadStatistics();
  }, [refreshTrigger, searchQuery, filterDegree, filterCategory, currentPage]);

  // Przekazuj filtry do komponentu rodzica (HazardousDegrees)
  useEffect(() => {
    if (onFiltersChange) {
      const filters = {};
      if (searchQuery) filters.search = searchQuery;
      if (filterDegree) filters.stopien = filterDegree;
      if (filterCategory) filters.kategoria = filterCategory;
      onFiltersChange(filters);
    }
  }, [searchQuery, filterDegree, filterCategory, onFiltersChange]);

  const loadRecords = async () => {
    setLoading(true);
    try {
      // TODO: Zastąp wywołaniem właściwego API
      // const params = {
      //   skip: currentPage * itemsPerPage,
      //   limit: itemsPerPage,
      //   ...(searchQuery    && { search:    searchQuery }),
      //   ...(filterDegree   && { stopien:   filterDegree }),
      //   ...(filterCategory && { kategoria: filterCategory }),
      // };
      // const data = await hazardousDegreesAPI.getAll(params);
      // setRecords(data.records || []);
      //
      // Zbierz unikalne wartości do filtrów
      // const allDegrees    = [...new Set(data.records.map(r => r.stopien))];
      // const allCategories = [...new Set(data.records.map(r => r.kategoria))];
      // setDegrees(allDegrees);
      // setCategories(allCategories);

      // Tymczasowo puste dane - backend do podłączenia
      setRecords([]);
      setDegrees([]);
      setCategories([]);
    } catch (error) {
      console.error("Błąd ładowania stopni szkodliwości:", error);
      alert("Nie udało się załadować danych");
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      // TODO: await hazardousDegreesAPI.getStatistics();
      // setStatistics(data);

      // Tymczasowe dane statystyk
      setStatistics(null);
    } catch (error) {
      console.error("Błąd ładowania statystyk:", error);
    }
  };

  const handleDeleteRecord = async (recordId, name) => {
    if (!window.confirm(`Czy na pewno chcesz usunąć rekord: ${name}?`)) return;
    try {
      // TODO: await hazardousDegreesAPI.delete(recordId);
      loadRecords();
      loadStatistics();
    } catch (error) {
      console.error("Błąd usuwania rekordu:", error);
      alert("Nie udało się usunąć rekordu");
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setFilterDegree("");
    setFilterCategory("");
    setCurrentPage(0);
  };

  const hasActiveFilters = searchQuery || filterDegree || filterCategory;

  return (
    <div className="hazardous-degrees-container">
      {/* ─── STATYSTYKI ─── */}
      {statistics && (
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-icon">☣️</div>
            <div className="stat-info">
              <div className="stat-label">Łącznie rekordów</div>
              <div className="stat-number">{statistics.total_records}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-info">
              <div className="stat-label">Stopni</div>
              <div className="stat-number">
                {statistics.by_degree?.length || 0}
              </div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🗂️</div>
            <div className="stat-info">
              <div className="stat-label">Kategorii</div>
              <div className="stat-number">
                {statistics.by_category?.length || 0}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ─── KONTROLKI / FILTRY ─── */}
      <div className="degrees-header">
        <h2>Lista stopni szkodliwości</h2>

        <div className="degrees-controls">
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
            value={filterDegree}
            onChange={(e) => {
              setFilterDegree(e.target.value);
              setCurrentPage(0);
            }}
            className="filter-select"
          >
            <option value="">Wszystkie stopnie</option>
            {degrees.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>

          <select
            value={filterCategory}
            onChange={(e) => {
              setFilterCategory(e.target.value);
              setCurrentPage(0);
            }}
            className="filter-select"
          >
            <option value="">Wszystkie kategorie</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          {hasActiveFilters && (
            <button onClick={clearFilters} className="btn-clear-filters">
              Wyczyść filtry
            </button>
          )}
        </div>
      </div>

      {/* ─── LISTA / STANY ─── */}
      {loading ? (
        <div className="loading">Ładowanie danych...</div>
      ) : records.length === 0 ? (
        <div className="no-data">
          <p>Brak rekordów do wyświetlenia</p>
          <p className="hint">Dodaj pierwszy rekord lub podłącz backend</p>
        </div>
      ) : (
        <>
          {/* ─── GRID KART ─── */}
          <div className="degrees-grid">
            {records.map((record) => (
              <div key={record.id} className="degree-card">
                {/* Awatar / inicjały */}
                <div className="degree-avatar">
                  {record.nazwisko_imie
                    ? record.nazwisko_imie
                        .split(" ")
                        .map((n) => n[0])
                        .join("")
                        .slice(0, 2)
                    : "??"}
                </div>

                <div className="degree-info">
                  <h3 className="degree-name">
                    {/* TODO: Dostosuj pole do modelu danych */}
                    {record.nazwisko_imie}
                  </h3>
                  <div className="degree-details">
                    <div className="detail-item">
                      <span className="detail-icon">☣️</span>
                      <span>{record.stopien}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">🗂️</span>
                      <span>{record.kategoria}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-icon">📅</span>
                      <span>{record.data}</span>
                    </div>
                  </div>
                </div>

                <div className="degree-actions">
                  <button
                    onClick={() => onEditRecord(record)}
                    className="btn-edit"
                    title="Edytuj"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() =>
                      handleDeleteRecord(record.id, record.nazwisko_imie)
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

          {/* ─── PAGINACJA ─── */}
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

export default HazardousDegreesList;
