from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Dict, Any
import uuid
from ..core.database import Base

class SurgicalPackage(Base):
    __tablename__ = "surgical_packages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quote_id = Column(String(36), ForeignKey('quotes.id', ondelete='CASCADE'))
    medications_included = Column(JSON, default=list)
    postoperative_care = Column(JSON, default=list)
    hospital_stay_nights = Column(Integer, default=0)
    special_equipment = Column(JSON, default=list)
    dietary_plan = Column(Boolean, default=False)
    additional_services = Column(JSON, default=list)

    # Relación con Quote
    quote = relationship("Quote", back_populates="surgical_package")

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Patient Information
    patient_id = Column(String(50), nullable=True)
    patient_age = Column(Integer, nullable=True)
    patient_phone = Column(String(20), nullable=True)
    patient_email = Column(String(100), nullable=True)
    
    # Procedure Information
    procedure_name = Column(String(200), nullable=False)
    procedure_code = Column(String(50), nullable=True)
    procedure_description = Column(Text, nullable=True)
    
    # Surgeon Information
    surgeon_name = Column(String(100), nullable=True)
    surgeon_specialty = Column(String(100), nullable=True)
    
    # Surgery Details
    surgery_duration_hours = Column(Integer, nullable=False)
    anesthesia_type = Column(String(50), nullable=False)
    additional_equipment = Column(JSON, default=list)
    additional_materials = Column(JSON, default=list)
    is_ambulatory = Column(Boolean, default=True)
    hospital_nights = Column(Integer, default=0)
    
    # Cost Breakdown
    facility_fee = Column(Float, nullable=False)
    equipment_costs = Column(Float, nullable=False)
    anesthesia_fee = Column(Float, default=0.0)
    other_costs = Column(Float, default=0.0)
    total_cost = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_by = Column(String(100), nullable=False)
    status = Column(String(20), default="borrador")
    notes = Column(Text, nullable=True)

    # Relación con SurgicalPackage
    surgical_package = relationship("SurgicalPackage", uselist=False, back_populates="quote", cascade="all, delete-orphan")
