from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
from pathlib import Path

# Dodaj parent directory do path żeby zaimportować database
sys.path.append(str(Path(__file__).parent.parent))
from database import Base

class ImportedFile(Base):
    """Model dla zaimportowanych plików Excel"""
    __tablename__ = "imported_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    imported_at = Column(DateTime, default=datetime.utcnow)
    rows_count = Column(Integer, default=0)
    status = Column(String(50), default="completed")  # completed, processing, error
    notes = Column(Text)
    
    # Relacja do danych
    swd_records = relationship("SWDRecord", back_populates="file", cascade="all, delete-orphan")

class SWDRecord(Base):
    """
    Model dla pojedynczego rekordu z zestawienia udziału SWD
    Dostosuj pola do struktury danych z biblioteki zestawienie-udzialu-swd
    """
    __tablename__ = "swd_records"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("imported_files.id"), nullable=False)
    
    # Przykładowe pola - dostosuj do rzeczywistej struktury danych
    # z biblioteki zestawienie-udzialu-swd
    nazwa_swd = Column(String(255))
    kod_swd = Column(String(100))
    kategoria = Column(String(100))
    wartosc = Column(Float)
    jednostka = Column(String(50))
    data_pomiaru = Column(String(100))
    uwagi = Column(Text)
    
    # Metadane
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacja do pliku
    file = relationship("ImportedFile", back_populates="swd_records")
    
    def to_dict(self):
        """Konwersja do słownika dla API"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "nazwa_swd": self.nazwa_swd,
            "kod_swd": self.kod_swd,
            "kategoria": self.kategoria,
            "wartosc": self.wartosc,
            "jednostka": self.jednostka,
            "data_pomiaru": self.data_pomiaru,
            "uwagi": self.uwagi,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }