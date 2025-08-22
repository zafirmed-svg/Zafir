from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.orm import relationship
import json
from datetime import datetime
from core.database import Base

class JSONType(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

class Quote(Base):
    __tablename__ = 'quotes'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(100))
    patient_age = Column(Integer)
    patient_phone = Column(String(20))
    patient_email = Column(String(100))
    procedure_name = Column(String(200))
    procedure_code = Column(String(50))
    procedure_description = Column(String(1000))
    surgeon_name = Column(String(100))
    surgeon_specialty = Column(String(100))
    facility_fee = Column(Float)
    equipment_costs = Column(Float)
    anesthesia_fee = Column(Float)
    other_costs = Column(Float)
    surgery_duration_hours = Column(Integer)
    created_by = Column(String(100))
    notes = Column(String(1000))
    surgical_package = Column(JSONType)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='borrador')

class SurgicalPackage(Base):
    __tablename__ = 'surgical_packages'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type = Column(String(50))
    price = Column(Float)
    description = Column(String(500))
    services = Column(String(1000))  # Stored as comma-separated string
    created_at = Column(DateTime, default=datetime.utcnow)

class Procedure(Base):
    __tablename__ = 'procedures'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(500))
    estimated_time = Column(Integer)  # en minutos
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Surgeon(Base):
    __tablename__ = 'surgeons'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    specialty = Column(String(100))
    license_number = Column(String(50))
    contact_info = Column(JSONType)
    created_at = Column(DateTime, default=datetime.utcnow)
