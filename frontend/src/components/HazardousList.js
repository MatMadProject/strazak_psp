import React, { useState, useEffect, useCallback } from "react";
import { hazardousRecordsAPI } from "../services/api";
import { hazardousDegreesAPI } from "../services/api";
import "./HazardousList.css";

function HazardousList({ file, subTab, onBack, onEditRecord, onAddRecord }) {
  const [records, setRecords] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [degrees, setDegrees] = useState([]);
  const [firefighters, setFirefighters] = useState([]);
  const [filterFirefighter, setFilterFirefighter] = useState("");
  const [filterUnassigned, setFilterUnassigned] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [itemsPerPage] = useState(100);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");
  const [assigningId, setAssigningId] = useState(null);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [filterEligible, setFilterEligible] = useState(false);

  const loadRecords = useCallback(async () => {
    if (!file?.id) return;
    setLoading(true);
    try {
      const params = {
        skip: currentPage * itemsPerPage,
        limit: itemsPerPage,
        ...(filterFirefighter && { firefighter: filterFirefighter }),
        ...(filterUnassigned && { only_unassigned: true }),
        ...(filterEligible && { only_eligible: true }),
        ...(dateFrom && { date_from: dateFrom }),
        ...(dateTo && { date_to: dateTo }),
        ...(sortBy && { sort_by: sortBy, sort_order: sortOrder }),
      };
      const data = await hazardousRecordsAPI.getRecords(file.id, params);
      setRecords(data.records || []);
      setTotalCount(data.total_count || 0);
    } catch (error) {
      console.error("Błąd ładowania rekordów:", error);
      alert("Nie udało się załadować rekordów");
    } finally {
      setLoading(false);
    }
  }, [
    file,
    currentPage,
    itemsPerPage,
    filterFirefighter,
    filterUnassigned,
    filterEligible,
    dateFrom,
    dateTo,
    sortBy,
    sortOrder,
  ]);

  const loadAuxData = useCallback(async () => {
    if (!file?.id) return;
    try {
      const [firefightersData, degreesData] = await Promise.all([
        hazardousRecordsAPI.getFirefighters(file.id),
        hazardousDegreesAPI.getAll({ limit: 1000 }),
      ]);
      setFirefighters(firefightersData.firefighters || []);
      setDegrees(degreesData.records || []);
    } catch (error) {
      console.error("Błąd ładowania danych pomocniczych:", error);
    }
  }, [file]);

  useEffect(() => {
    loadRecords();
  }, [loadRecords]);
  useEffect(() => {
    loadAuxData();
  }, [loadAuxData]);

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder((o) => (o === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
    setCurrentPage(0);
  };

  const SortIcon = ({ col }) => {
    if (sortBy !== col) return <span className="hl-sort-icon">↕</span>;
    return (
      <span className="hl-sort-icon hl-sort-icon--active">
        {sortOrder === "asc" ? "↑" : "↓"}
      </span>
    );
  };

  const handleAssignDegree = async (recordId, degreeId) => {
    setAssigningId(recordId);
    try {
      await hazardousRecordsAPI.assignDegree(
        recordId,
        degreeId ? parseInt(degreeId) : null,
      );
      setRecords((prev) =>
        prev.map((r) => {
          if (r.id !== recordId) return r;
          const degree =
            degrees.find((d) => d.id === parseInt(degreeId)) || null;
          return {
            ...r,
            hazardous_degree_id: degreeId ? parseInt(degreeId) : null,
            hazardous_degree: degree,
          };
        }),
      );
    } catch (error) {
      console.error("Błąd przypisania stopnia:", error);
      alert("Nie udało się przypisać stopnia szkodliwości");
    } finally {
      setAssigningId(null);
    }
  };

  const handleDeleteRecord = async (record) => {
    if (
      !window.confirm(
        `Czy na pewno chcesz usunąć rekord dla ${record.nazwisko_imie}?`,
      )
    )
      return;
    try {
      await hazardousRecordsAPI.deleteRecord(record.id);
      loadRecords();
      loadAuxData();
    } catch (error) {
      console.error("Błąd usuwania:", error);
      alert("Nie udało się usunąć rekordu");
    }
  };

  const clearFilters = () => {
    setFilterFirefighter("");
    setFilterUnassigned(false);
    setFilterEligible(false);
    setDateFrom("");
    setDateTo("");
    setCurrentPage(0);
  };

  const hasActiveFilters =
    filterFirefighter ||
    filterUnassigned ||
    filterEligible ||
    dateFrom ||
    dateTo;

  const formatDateTime = (iso) => {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString("pl-PL", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  };

  return (
    <div className="hl-container">
      {/* ─── HEADER ─── */}
      <div className="hl-header">
        <div className="hl-header-left">
          <button className="hl-btn-back" onClick={onBack}>
            ← Powrót
          </button>
          <div className="hl-header-info">
            <h2>☣️ Dodatek Szkodliwy</h2>
            <span className="hl-file-badge">📄 {file?.filename}</span>
          </div>
        </div>
        <div className="hl-header-right">
          <button className="hl-btn-add" onClick={onAddRecord}>
            ✚ Dodaj rekord
          </button>
        </div>
      </div>

      {/* ─── FILTRY ─── */}
      <div className="hl-controls">
        <div className="hl-control-group">
          <label>👤 Osoba:</label>
          <select
            value={filterFirefighter}
            onChange={(e) => {
              setFilterFirefighter(e.target.value);
              setCurrentPage(0);
            }}
            className="hl-filter-select"
          >
            <option value="">Wszystkie osoby</option>
            {firefighters.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>

        <div className="hl-control-group">
          <label className="hl-checkbox-label">
            <input
              type="checkbox"
              checked={filterUnassigned}
              onChange={(e) => {
                setFilterUnassigned(e.target.checked);
                setCurrentPage(0);
              }}
            />
            Tylko bez stopnia szkodliwości
          </label>
        </div>

        <div className="hl-control-group">
          <label className="hl-checkbox-label">
            <input
              type="checkbox"
              checked={filterEligible}
              onChange={(e) => {
                setFilterEligible(e.target.checked);
                setCurrentPage(0);
              }}
            />
            Tylko zaliczone do dodatku
          </label>
        </div>

        <div className="hl-control-group hl-date-filter">
          <label>📅 Data od:</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => {
              setDateFrom(e.target.value);
              setCurrentPage(0);
            }}
            className="hl-date-input"
          />
          <label>do:</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => {
              setDateTo(e.target.value);
              setCurrentPage(0);
            }}
            className="hl-date-input"
          />
        </div>

        {hasActiveFilters && (
          <button className="hl-btn-clear" onClick={clearFilters}>
            ✕ Wyczyść filtry
          </button>
        )}

        <span className="hl-records-count">
          {totalCount} rekordów{hasActiveFilters ? " (filtrowane)" : ""}
        </span>
      </div>

      {/* ─── TABELA ─── */}
      {loading ? (
        <div className="hl-loading">Ładowanie danych...</div>
      ) : records.length === 0 ? (
        <div className="hl-empty">
          <div className="hl-empty-icon">📭</div>
          <p>Brak rekordów do wyświetlenia</p>
          <p className="hl-empty-hint">
            {hasActiveFilters
              ? "Spróbuj zmienić lub wyczyścić filtry"
              : "Plik nie zawiera rekordów"}
          </p>
        </div>
      ) : (
        <>
          <div className="hl-table-wrapper">
            <table className="hl-table">
              <thead>
                <tr>
                  <th
                    className="hl-sortable"
                    onClick={() => handleSort("nazwisko_imie")}
                  >
                    Nazwisko i imię <SortIcon col="nazwisko_imie" />
                  </th>
                  <th
                    className="hl-sortable"
                    onClick={() => handleSort("funkcja")}
                  >
                    Funkcja <SortIcon col="funkcja" />
                  </th>
                  <th
                    className="hl-sortable"
                    onClick={() => handleSort("nr_meldunku")}
                  >
                    Nr meldunku <SortIcon col="nr_meldunku" />
                  </th>
                  <th>Czas od</th>
                  <th>Czas do</th>
                  <th
                    className="hl-sortable"
                    onClick={() => handleSort("czas_udzialu")}
                  >
                    Czas udziału <SortIcon col="czas_udzialu" />
                  </th>
                  <th>P / MZ / AF</th>
                  <th className="hl-col-degree">Stopień szkodliwości</th>
                  <th>Akcje</th>
                </tr>
              </thead>
              <tbody>
                {records.map((record) => (
                  <tr
                    key={record.id}
                    className={
                      record.hazardous_degree_id
                        ? "hl-row-assigned"
                        : "hl-row-unassigned"
                    }
                  >
                    <td className="hl-cell-name">
                      {record.nazwisko_imie || "—"}
                    </td>
                    <td>{record.funkcja || "—"}</td>
                    <td className="hl-cell-mono">
                      {record.nr_meldunku || "—"}
                    </td>
                    <td className="hl-cell-date">
                      {formatDateTime(record.czas_od)}
                    </td>
                    <td className="hl-cell-date">
                      {formatDateTime(record.czas_do)}
                    </td>
                    <td className="hl-cell-center">
                      {record.czas_udzialu || "—"}
                    </td>
                    <td className="hl-cell-flags">
                      {record.p && (
                        <span className="hl-flag hl-flag-p" title="P">
                          P
                        </span>
                      )}
                      {record.mz && (
                        <span className="hl-flag hl-flag-mz" title="MZ">
                          MZ
                        </span>
                      )}
                      {record.af && (
                        <span className="hl-flag hl-flag-af" title="AF">
                          AF
                        </span>
                      )}
                    </td>
                    <td className="hl-cell-degree">
                      <div className="hl-degree-wrapper">
                        <select
                          value={record.hazardous_degree_id || ""}
                          onChange={(e) =>
                            handleAssignDegree(record.id, e.target.value)
                          }
                          disabled={assigningId === record.id}
                          className={`hl-degree-select ${record.hazardous_degree_id ? "hl-degree-select--assigned" : "hl-degree-select--empty"}`}
                          title={
                            record.hazardous_degree
                              ? record.hazardous_degree.opis
                              : "Brak przypisanego stopnia"
                          }
                        >
                          <option value="">— brak —</option>
                          {degrees.map((d) => (
                            <option key={d.id} value={d.id}>
                              {d.stopien}.{d.punkt} —{" "}
                              {d.opis.length > 50
                                ? d.opis.slice(0, 50) + "…"
                                : d.opis}
                            </option>
                          ))}
                        </select>
                        {assigningId === record.id && (
                          <span className="hl-saving">⏳</span>
                        )}
                      </div>
                    </td>
                    <td className="hl-cell-actions">
                      <button
                        onClick={() => onEditRecord(record)}
                        className="hl-btn-edit"
                        title="Edytuj"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDeleteRecord(record)}
                        className="hl-btn-delete"
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

          {/* ─── PAGINACJA ─── */}
          <div className="hl-pagination">
            <button
              className="hl-btn-page"
              onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
              disabled={currentPage === 0}
            >
              ← Poprzednia
            </button>
            <span className="hl-page-info">
              Strona {currentPage + 1} · {records.length} z {totalCount}{" "}
              rekordów
            </span>
            <button
              className="hl-btn-page"
              onClick={() => setCurrentPage((p) => p + 1)}
              disabled={records.length < itemsPerPage}
            >
              Następna →
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default HazardousList;
