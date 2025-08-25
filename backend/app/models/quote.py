from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class SurgicalPackage(BaseModel):
    medications_included: Optional[List[str]] = []
    postoperative_care: Optional[List[str]] = []
    hospital_stay_nights: Optional[int] = 0
    special_equipment: Optional[List[str]] = []
    dietary_plan: Optional[bool] = False
    additional_services: Optional[List[str]] = []

class Quote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Patient Information
    patient_id: Optional[str] = None
    patient_age: Optional[int] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    
    # Procedure Information
    procedure_name: str
    procedure_code: Optional[str] = None
    procedure_description: Optional[str] = None
    
    # Surgeon Information
    surgeon_name: Optional[str] = None
    surgeon_specialty: Optional[str] = None
    
    # Surgery Details
    surgery_duration_hours: int
    anesthesia_type: str
    additional_equipment: Optional[List[str]] = []
    additional_materials: Optional[List[str]] = []
    is_ambulatory: bool = True
    hospital_nights: Optional[int] = 0
    
    # Cost Breakdown
    facility_fee: float
    equipment_costs: float
    anesthesia_fee: Optional[float] = 0.0
    other_costs: Optional[float] = 0.0
    total_cost: float
    
    # Surgical Package Details
    surgical_package: Optional[SurgicalPackage] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    status: str = "borrador"
    notes: Optional[str] = None

class QuoteCreate(BaseModel):
    patient_id: Optional[str] = None
    patient_age: Optional[int] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    procedure_name: str
    procedure_code: Optional[str] = None
    procedure_description: Optional[str] = None
    surgeon_name: Optional[str] = None
    surgeon_specialty: Optional[str] = None
    surgery_duration_hours: int
    anesthesia_type: str
    additional_equipment: Optional[List[str]] = []
    additional_materials: Optional[List[str]] = []
    is_ambulatory: bool = True
    hospital_nights: Optional[int] = 0
    facility_fee: float
    equipment_costs: float
    anesthesia_fee: Optional[float] = 0.0
    other_costs: Optional[float] = 0.0
    surgical_package: Optional[SurgicalPackage] = None
    created_by: str
    notes: Optional[str] = None

class PricingSuggestion(BaseModel):
    procedure_name: str
    avg_facility_fee: float
    avg_equipment_costs: float
    avg_total_cost: float
    quote_count: int
    suggested_total: float

class PDFProcessResult(BaseModel):
    success: bool
    message: str
    quotes_created: int
    extracted_data: Optional[dict] = None
    errors: Optional[List[str]] = None
