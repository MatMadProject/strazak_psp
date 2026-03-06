import React, { useState } from "react";
import HazardousDegreesList from "./HazardousDegreesList";
import HazardousDegreesEditor from "./HazardousDegreesEditor";
import HazardousDegreesFileEditor from "./HazardousDegreesFileEditor";
import "./HazardousDegrees.css";

/**
 * HazardousDegrees.js
 *
 * handleImport → setIsImporting(true) → renderuje HazardousDegreesFileEditor
 * handleAddNew → setIsAddingNew(true) → renderuje HazardousDegreesEditor
 */
function HazardousDegrees() {
  const [editingRecord, setEditingRecord] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [currentFilters, setCurrentFilters] = useState({});

  const handleAddNew = () => setIsAddingNew(true);

  const handleImport = () => setIsImporting(true);

  const handleEditRecord = (record) => setEditingRecord(record);

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
      <HazardousDegreesList
        onEditRecord={handleEditRecord}
        refreshTrigger={refreshTrigger}
        onFiltersChange={setCurrentFilters}
        onAddNew={handleAddNew}
        onImportClick={handleImport}
      />

      {/* Modal edytora rekordu — aktywny przy dodawaniu i edycji */}
      {(editingRecord || isAddingNew) && (
        <HazardousDegreesEditor
          record={editingRecord}
          onClose={handleCloseEditor}
          onSave={handleSave}
        />
      )}

      {/* Modal importu Excel — identyczny wzorzec jak FirefighterFileEditor */}
      {isImporting && (
        <HazardousDegreesFileEditor
          onClose={handleCloseEditor}
          onSuccess={handleSave}
        />
      )}
    </div>
  );
}

export default HazardousDegrees;
