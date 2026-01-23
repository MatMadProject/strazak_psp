from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
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
    Dostosowany do rzeczywistej struktury danych
    """
    __tablename__ = "swd_records"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("imported_files.id"), nullable=False)
    
    # Dane z pliku Excel - DOSTOSOWANE DO TWOJEJ STRUKTURY
    nazwisko_imie = Column(String(255))
    stopien = Column(String(100))
    p = Column(String(10))  # String bo może być "1" lub inna wartość
    mz = Column(String(10))
    af = Column(String(10))
    zaliczono_do_emerytury = Column(String(10))
    nr_meldunku = Column(String(100))
    czas_rozp_zdarzenia = Column(String(100))  # ZMIENIONE NA STRING zamiast DateTime
    funkcja = Column(String(100))
    
    # Metadane - te są automatyczne
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacja do pliku
    file = relationship("ImportedFile", back_populates="swd_records")
    
    def to_dict(self):
        """Konwersja do słownika dla API"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "nazwisko_imie": self.nazwisko_imie,
            "stopien": self.stopien,
            "p": self.p,
            "mz": self.mz,
            "af": self.af,
            "zaliczono_do_emerytury": self.zaliczono_do_emerytury,
            "nr_meldunku": self.nr_meldunku,
            "czas_rozp_zdarzenia": self.czas_rozp_zdarzenia,
            "funkcja": self.funkcja,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
class Firefighter(Base):
    """
    Model dla danych o strażaku.
    """
    __tablename__ = "firefighters"
    
    id = Column(Integer, primary_key=True, index=True)
    nazwisko_imie = Column(String(255), nullable=False)
    stopien = Column(String(100), nullable=False)
    stanowisko = Column(String(100), nullable=False)
    jednostka = Column(String(100), nullable=False)

    # Metadane - te są automatyczne
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Konwersja do słownika dla API"""
        return {
            "id": self.id,
            "nazwisko_imie": self.nazwisko_imie,
            "stopien": self.stopien,
            "stanowisko": self.stanowisko,
            "jednostka": self.jednostka,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }