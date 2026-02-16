import axios from "axios";

// Automatycznie używa proxy z package.json w dev mode
// W produkcji (desktop) komunikuje się z localhost:8000
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Files API
export const filesAPI = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/files/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getAllFiles: async () => {
    const response = await api.get("/api/files/");
    return response.data;
  },

  getFileDetails: async (fileId) => {
    const response = await api.get(`/api/files/${fileId}`);
    return response.data;
  },

  deleteFile: async (fileId) => {
    const response = await api.delete(`/api/files/${fileId}`);
    return response.data;
  },

  getFilePreview: async (fileId) => {
    const response = await api.get(`/api/files/${fileId}/preview`);
    return response.data;
  },
};

// Data API
export const dataAPI = {
  getRecords: async (params = {}) => {
    const response = await api.get("/api/data/records", { params });
    return response.data;
  },

  getRecord: async (recordId) => {
    const response = await api.get(`/api/data/records/${recordId}`);
    return response.data;
  },

  updateRecord: async (recordId, data) => {
    const response = await api.put(`/api/data/records/${recordId}`, data);
    return response.data;
  },

  deleteRecord: async (recordId) => {
    const response = await api.delete(`/api/data/records/${recordId}`);
    return response.data;
  },

  getStatistics: async () => {
    const response = await api.get("/api/data/statistics");
    return response.data;
  },

  getFileRecords: async (fileId, params = {}) => {
    const response = await api.get(`/api/data/files/${fileId}/records`, {
      params,
    });
    return response.data;
  },

  getFirefightersInFile: async (fileId) => {
    const response = await api.get(`/api/data/files/${fileId}/firefighters`);
    return response.data;
  },

  createRecord: async (fileId, data) => {
    const response = await api.post(`api/data/files/${fileId}/records`, data);
    return response.data;
  },

  exportDeparturesToExcel: async (fileId, filters = {}) => {
    const response = await api.get(`/api/data/files/${fileId}/export/excel`, {
      params: filters,
      responseType: "blob",
    });

    // Wyciągnij nazwę pliku z nagłówka Content-Disposition
    const contentDisposition = response.headers["content-disposition"];
    let filename = `wyjazdy_${new Date().toISOString().split("T")[0]}.xlsx`;

    console.log("Content-Disposition:", contentDisposition); // Debug

    if (contentDisposition) {
      // RFC 5987: filename*=UTF-8''encoded_filename
      const filenameStarMatch = contentDisposition.match(
        /filename\*=UTF-8''([^;]+)/,
      );
      if (filenameStarMatch && filenameStarMatch[1]) {
        filename = decodeURIComponent(filenameStarMatch[1]);
      } else {
        // Fallback dla starego formatu
        const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].trim().replace(/['"]/g, "");
        }
      }
    }

    console.log("Extracted filename:", filename); // Debug

    return {
      blob: response.data,
      filename: filename,
    };
  },

  exportDeparturesToCSV: async (fileId, filters = {}) => {
    const response = await api.get(`/api/data/files/${fileId}/export/csv`, {
      params: filters,
      responseType: "blob",
    });

    // Wyciągnij nazwę pliku z nagłówka Content-Disposition
    const contentDisposition = response.headers["content-disposition"];
    let filename = `wyjazdy_${new Date().toISOString().split("T")[0]}.csv`;

    console.log("Content-Disposition:", contentDisposition); // Debug

    if (contentDisposition) {
      // RFC 5987: filename*=UTF-8''encoded_filename
      const filenameStarMatch = contentDisposition.match(
        /filename\*=UTF-8''([^;]+)/,
      );
      if (filenameStarMatch && filenameStarMatch[1]) {
        filename = decodeURIComponent(filenameStarMatch[1]);
      } else {
        // Fallback dla starego formatu
        const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].trim().replace(/['"]/g, "");
        }
      }
    }

    console.log("Extracted filename:", filename); // Debug

    return {
      blob: response.data,
      filename: filename,
    };
  },

  generateDocument: async (fileId, format, filters = {}) => {
    const response = await api.get(
      `/api/data/files/${fileId}/generate-document/${format}`,
      {
        params: filters,
        responseType: "blob",
      },
    );

    // Wyciągnij nazwę pliku z nagłówka Content-Disposition
    const contentDisposition = response.headers["content-disposition"];
    let filename = `karta_wyjazdow_${new Date().toISOString().split("T")[0]}.${format}`;

    if (contentDisposition) {
      const filenameStarMatch = contentDisposition.match(
        /filename\*=UTF-8''([^;]+)/,
      );
      if (filenameStarMatch && filenameStarMatch[1]) {
        filename = decodeURIComponent(filenameStarMatch[1]);
      }
    }

    return {
      blob: response.data,
      filename: filename,
    };
  },
};

// Firefighters API
export const firefightersAPI = {
  getAllFirefighters: async (params = {}) => {
    const response = await api.get("/api/firefighters/", { params });
    return response.data;
  },

  getFirefighter: async (firefighterId) => {
    const response = await api.get(`/api/firefighters/${firefighterId}`);
    return response.data;
  },

  createFirefighter: async (data) => {
    const response = await api.post("/api/firefighters/", data);
    return response.data;
  },

  updateFirefighter: async (firefighterId, data) => {
    const response = await api.put(`/api/firefighters/${firefighterId}`, data);
    return response.data;
  },

  deleteFirefighter: async (firefighterId) => {
    const response = await api.delete(`/api/firefighters/${firefighterId}`);
    return response.data;
  },

  getStatistics: async () => {
    const response = await api.get("/api/firefighters/statistics");
    return response.data;
  },

  downloadTemplate: async () => {
    const response = await api.get("/api/firefighters/template/download", {
      responseType: "blob",
    });
    return response.data;
  },

  importFromExcel: async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/firefighters/import", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  exportToExcel: async (filters = {}) => {
    const response = await api.get("/api/firefighters/export/excel", {
      params: filters,
      responseType: "blob",
    });
    return response.data;
  },

  exportToCSV: async (filters = {}) => {
    const response = await api.get("/api/firefighters/export/csv", {
      params: filters,
      responseType: "blob",
    });
    return response.data;
  },
};
//Settings API
export const settingsAPI = {
  getSettings: async () => {
    const response = await api.get("/api/settings/");
    return response.data;
  },

  updateSettings: async (settings) => {
    const response = await api.post("/api/settings/", settings);
    return response.data;
  },

  getCurrentDatabase: async () => {
    const response = await api.get("/api/settings/current-database");
    return response.data;
  },

  browseDatabaseFile: async () => {
    const response = await api.get("/api/settings/browse-database/");
    return response.data;
  },

  browseDatabaseFolder: async () => {
    const response = await api.get("/api/settings/browse-folder/");
    return response.data;
  },
};
export default api;
