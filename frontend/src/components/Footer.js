import React, { useState, useEffect } from "react";
import { systemAPI } from "../services/api";
import "./Footer.css";

function Footer() {
  const [appInfo, setAppInfo] = useState(null);

  useEffect(() => {
    loadAppInfo();
  }, []);

  const loadAppInfo = async () => {
    try {
      const info = await systemAPI.getAppInfo();
      setAppInfo(info);
    } catch (error) {
      console.error("Błąd ładowania informacji o aplikacji:", error);
    }
  };

  if (!appInfo) {
    return null; // Nie pokazuj stopki jeśli brak danych
  }

  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-left">
          <span className="footer-app-name">{appInfo.app_name}</span>
          <span className="footer-version">v{appInfo.version}</span>
        </div>
        <div className="footer-center">
          © {currentYear} {appInfo.company}. Wszelkie prawa zastrzeżone.
        </div>
        <div className="footer-right">
          {appInfo.is_desktop && <span className="footer-badge">Desktop</span>}
        </div>
      </div>
    </footer>
  );
}

export default Footer;
