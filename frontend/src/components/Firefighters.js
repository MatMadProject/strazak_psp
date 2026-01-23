import React, { useState } from "react";
import FirefightersList from "./FirefightersList";
import FirefighterEditor from "./FirefighterEditor";
import "./Firefighters.css";

function Firefighters() {
  const [editingFirefighter, setEditingFirefighter] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleAddNew = () => {
    setIsAddingNew(true);
  };

  const handleEditFirefighter = (firefighter) => {
    setEditingFirefighter(firefighter);
  };

  const handleCloseEditor = () => {
    setEditingFirefighter(null);
    setIsAddingNew(false);
  };

  const handleSave = () => {
    setEditingFirefighter(null);
    setIsAddingNew(false);
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="firefighters-page">
      <div className="firefighters-page-header">
        <div>
          <h1>👨‍🚒 Strażacy</h1>
          <p className="page-subtitle">Zarządzanie danymi strażaków</p>
        </div>
        <button onClick={handleAddNew} className="btn-add-new">
          📄 Export do pliku
        </button>
        <button onClick={handleAddNew} className="btn-add-new">
          ✚ Dodaj z pliku
        </button>
        <button onClick={handleAddNew} className="btn-add-new">
          ✚ Dodaj strażaka
        </button>
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
    </div>
  );
}

export default Firefighters;
