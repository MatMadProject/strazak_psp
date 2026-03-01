import React, { useState } from "react";
import HazardousDegreesList from "./HazardousDegreesList";
// import HazardousDegreesEditor from "./HazardousDegreesEditor";   // przyszły edytor
// import HazardousDegreesFileEditor from "./HazardousDegreesFileEditor"; // import Excel
import ExportButton from "./ExportButton";
import "./HazardousDegrees.css";

/**
 * HazardousDegrees.js
 * Główny komponent zakładki "Stopnie Szkodliwości".
 */
function HazardousDegrees() {
  const [editingRecord, setEditingRecord] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [currentFilters, setCurrentFilters] = useState({});

  const handleAddNew = () => {
    setIsAddingNew(true);
  };

  const handleImport = () => {
    setIsImporting(true);
  };

  const handleEditRecord = (record) => {
    setEditingRecord(record);
  };

  const handleCloseEditor = () => {
    setEditingRecord(null);
    setIsAddingNew(false);
    setIsImporting(false);
  };

  const handleSave = () => {
    setEditingRecord(null);
    setIsAddingNew(false);
    setIsImporting(false);
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="hazardous-degrees-page">
      <div className="hazardous-degrees-page-header">
        {/* <div>
          <h1>☣️ Stopnie Szkodliwości</h1>
          <p className="page-subtitle">Zarządzanie stopniami szkodliwości</p>
        </div> */}
        <div className="header-buttons">
          {/* TODO: podłącz ExportButton z właściwymi filtrami gdy API gotowe */}
          {/* <ExportButton filters={currentFilters} endpoint="hazardous-degrees" /> */}
          <button onClick={handleImport} className="btn-import">
            📥 Import z Excel
          </button>
          <button onClick={handleAddNew} className="btn-add-new">
            ✚ Dodaj stopień
          </button>
        </div>
      </div>

      <HazardousDegreesList
        onEditRecord={handleEditRecord}
        refreshTrigger={refreshTrigger}
        onFiltersChange={setCurrentFilters}
      />

      {/* TODO: Odkomentuj gdy HazardousDegreesEditor będzie gotowy */}
      {/* {(editingRecord || isAddingNew) && (
        <HazardousDegreesEditor
          record={editingRecord}
          onClose={handleCloseEditor}
          onSave={handleSave}
        />
      )} */}

      {/* TODO: Odkomentuj gdy HazardousDegreesFileEditor będzie gotowy */}
      {/* {isImporting && (
        <HazardousDegreesFileEditor
          onClose={handleCloseEditor}
          onSuccess={handleSave}
        />
      )} */}
    </div>
  );
}

export default HazardousDegrees;
