import React, { useState } from "react";
import FirefightersList from "./FirefightersList";
import FirefighterEditor from "./FirefighterEditor";
import FirefighterFileEditor from "./FirefighterFileEditor";
import ExportButton from "./ExportButton";
import "./Firefighters.css";

function Firefighters() {
  const [editingFirefighter, setEditingFirefighter] = useState(null);
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

  const handleEditFirefighter = (firefighter) => {
    setEditingFirefighter(firefighter);
  };

  const handleCloseEditor = () => {
    setEditingFirefighter(null);
    setIsAddingNew(false);
    setIsImporting(false);
  };

  const handleSave = () => {
    setEditingFirefighter(null);
    setIsAddingNew(false);
    setIsImporting(false);
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="firefighters-page">
      <div className="firefighters-page-header">
        {/* <div>
          <h1>👨‍🚒 Strażacy</h1>
          <p className="page-subtitle">Zarządzanie danymi strażaków</p>
        </div> */}
        <div className="header-buttons">
          <ExportButton filters={currentFilters} />
          <button onClick={handleImport} className="btn-import">
            📥 Import z Excel
          </button>
          <button onClick={handleAddNew} className="btn-add-new">
            ✚ Dodaj strażaka
          </button>
        </div>
      </div>

      <FirefightersList
        onEditFirefighter={handleEditFirefighter}
        refreshTrigger={refreshTrigger}
      />

      {(editingFirefighter || isAddingNew) && (
        <FirefighterEditor
          firefighter={editingFirefighter}
          onClose={handleCloseEditor}
          onSave={handleSave}
        />
      )}

      {isImporting && (
        <FirefighterFileEditor
          onClose={handleCloseEditor}
          onSuccess={handleSave}
        />
      )}
    </div>
  );
}

export default Firefighters;
