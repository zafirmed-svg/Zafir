from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date, time
from decimal import Decimal
import pdfplumber
import re
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper functions for MongoDB serialization
def prepare_for_mongo(data):
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item.get('created_at'), str):
        item['created_at'] = datetime.fromisoformat(item['created_at'])
    return item

# PDF Processing Functions
def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text from PDF using pdfplumber"""
    try:
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

def parse_quote_from_text(text: str) -> dict:
    """Parse quote information from extracted text using regex patterns"""
    quote_data = {
        "patient_id": None,
        "patient_age": None,
        "patient_phone": None,
        "patient_email": None,
        "procedure_name": "",
        "procedure_code": None,
        "procedure_description": None,
        "surgeon_name": "",
        "surgeon_specialty": None,
        "facility_fee": 0.0,
        "equipment_costs": 0.0,
        "anesthesia_fee": 0.0,
        "other_costs": 0.0,
        "surgery_duration_hours": 0,
        "anesthesia_type": "",
        "additional_equipment": [],
        "additional_materials": [],
        "is_ambulatory": True,
        "hospital_nights": 0,
        "created_by": "Importación PDF",
        "notes": "Cotización importada desde PDF",
        "surgical_package": {
            "medications_included": [],
            "postoperative_care": [],
            "hospital_stay_nights": 0,
            "special_equipment": [],
            "dietary_plan": False,
            "additional_services": []
        }
    }
    
    # Clean text for better parsing
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Patient ID patterns
    patient_id_patterns = [
        r'(?:paciente|patient|id|expediente|número)[\s:]*([A-Z0-9\-]+)',
        r'ID[\s:]*([A-Z0-9\-]+)',
        r'No\.?\s*([A-Z0-9\-]+)'
    ]
    for pattern in patient_id_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quote_data["patient_id"] = match.group(1).strip()
            break
    
    # Age patterns
    age_patterns = [
        r'(?:edad|age|años)[\s:]*(\d{1,3})',
        r'(\d{1,3})\s*(?:años|years old)'
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quote_data["patient_age"] = int(match.group(1))
            break
    
    # Phone patterns
    phone_patterns = [
        r'(?:teléfono|telefono|phone|tel)[\s:]*([0-9\-\s\(\)]+)',
        r'(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            phone = re.sub(r'[^\d]', '', match.group(1))
            if len(phone) >= 10:
                quote_data["patient_phone"] = match.group(1).strip()
            break
    
    # Email patterns
    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    match = re.search(email_pattern, text)
    if match:
        quote_data["patient_email"] = match.group(1).strip()
    
    # Procedure name patterns
    procedure_patterns = [
        r'(?:procedimiento|procedure|cirugía|surgery|operación)[\s:]*([^$\d\n]{10,80})',
        r'(?:reemplazo|replacement|bypass|apendicectomía|appendectomy)[\s\w]*',
        r'(?:artroscopia|laparoscopia|endoscopia)[\s\w]*'
    ]
    for pattern in procedure_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            procedure = match.group(0).strip()
            if len(procedure) > 5:
                quote_data["procedure_name"] = procedure[:80]
                break
    
    # Surgeon name patterns (optional)
    surgeon_patterns = [
        r'(?:dr\.?|doctor|dra\.?|doctora|cirujano|surgeon)[\s]*([A-Za-záéíóúñÁÉÍÓÚÑ\s]{5,40})',
        r'médico[\s:]*([A-Za-záéíóúñÁÉÍÓÚÑ\s]{5,40})'
    ]
    for pattern in surgeon_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            surgeon = match.group(1).strip()
            if len(surgeon) > 3:
                quote_data["surgeon_name"] = surgeon[:40]
                break
    
    # Duration patterns (hours only)
    duration_patterns = [
        r'(?:duración|duration|tiempo)[\s:]*(\d+)[\s]*(?:horas?|hours?|hrs?)',
        r'(\d+)[\s]*(?:horas?|hours?|hrs?)[\s]*(?:de[\s]*)?(?:cirugía|surgery|operación)',
        r'(?:cirugía|surgery)[\s]*(?:de[\s]*)?(\d+)[\s]*(?:horas?|hours?|hrs?)'
    ]
    for pattern in duration_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                hours = int(match.group(1))
                if 1 <= hours <= 24:
                    quote_data["surgery_duration_hours"] = hours
                    break
            except:
                continue
    
    # Anesthesia type patterns
    anesthesia_patterns = [
        r'(?:anestesia|anesthesia)[\s]*(?:general|epidural|regional|local|sedación)',
        r'(?:bloqueo|block)[\s]*(?:epidural|regional)',
        r'(?:sedación|sedation)[\s]*(?:básica|basic)?'
    ]
    for pattern in anesthesia_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quote_data["anesthesia_type"] = match.group(0).strip()
            break
    
    # Cost patterns (Mexican Pesos)
    cost_patterns = {
        "facility_fee": [
            r'(?:instalaciones|facilities|hospital)[\s:$]*(\$?[\d,]+\.?\d*)',
            r'(?:costo.*hospital)[\s:$]*(\$?[\d,]+\.?\d*)'
        ],
        "equipment_costs": [
            r'(?:equipos|equipment|instrumental)[\s:$]*(\$?[\d,]+\.?\d*)',
            r'(?:materiales|supplies)[\s:$]*(\$?[\d,]+\.?\d*)'
        ],
        "anesthesia_fee": [
            r'(?:anestesia|anesthesia)[\s:$]*(\$?[\d,]+\.?\d*)'
        ]
    }
    
    for cost_type, patterns in cost_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cost_str = match.group(1).replace('$', '').replace(',', '')
                try:
                    quote_data[cost_type] = float(cost_str)
                    break
                except ValueError:
                    continue
    
    # Total cost patterns
    total_patterns = [
        r'(?:total|costo total|total cost)[\s:$]*(\$?[\d,]+\.?\d*)',
        r'(?:suma|amount)[\s:$]*(\$?[\d,]+\.?\d*)'
    ]
    total_cost = 0
    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cost_str = match.group(1).replace('$', '').replace(',', '')
            try:
                total_cost = float(cost_str)
                break
            except ValueError:
                continue
    
    # If no individual costs found but total exists, distribute proportionally
    if total_cost > 0 and (quote_data["facility_fee"] + quote_data["equipment_costs"] + quote_data["anesthesia_fee"]) == 0:
        quote_data["facility_fee"] = total_cost * 0.6  # 60% facilities
        quote_data["equipment_costs"] = total_cost * 0.3  # 30% equipment
        quote_data["anesthesia_fee"] = total_cost * 0.1  # 10% anesthesia
    
    # Extract medications and services from text
    medication_keywords = ['antibiótico', 'analgésico', 'antiinflamatorio', 'medicamento', 'fármaco']
    for keyword in medication_keywords:
        if keyword in text.lower():
            quote_data["surgical_package"]["medications_included"].append(keyword.title())
    
    # Extract special equipment
    equipment_keywords = ['prótesis', 'implante', 'stent', 'marcapasos', 'dispositivo', 'laparoscopia', 'artroscopia']
    for keyword in equipment_keywords:
        if keyword in text.lower():
            quote_data["additional_equipment"].append(keyword.title())
    
    # Hospital stay patterns
    nights_patterns = [
        r'(\d+)\s*(?:noches?|nights?|días?|days?)\s*(?:hospitalización|hospital)',
        r'(?:hospitalización|hospital)[\s:]*(\d+)\s*(?:noches?|días?)',
        r'(?:ambulatori[ao]|outpatient)'
    ]
    for pattern in nights_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if 'ambulatori' in match.group(0).lower() or 'outpatient' in match.group(0).lower():
                quote_data["is_ambulatory"] = True
                quote_data["hospital_nights"] = 0
            else:
                nights = int(match.group(1)) if match.group(1).isdigit() else 0
                quote_data["hospital_nights"] = nights
                quote_data["is_ambulatory"] = nights == 0
            break
    
    return quote_data

# Define Models
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
    
    # Surgery Details - New Fields
    surgery_duration_hours: int
    anesthesia_type: str  # New field
    additional_equipment: Optional[List[str]] = []  # New field
    additional_materials: Optional[List[str]] = []  # New field
    is_ambulatory: bool = True  # New field
    hospital_nights: Optional[int] = 0  # New field
    
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
    anesthesia_type: str  # New field
    additional_equipment: Optional[List[str]] = []  # New field
    additional_materials: Optional[List[str]] = []  # New field
    is_ambulatory: bool = True  # New field
    hospital_nights: Optional[int] = 0  # New field
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

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Sistema de Gestión de Cotizaciones Quirúrgicas"}

@api_router.post("/upload-pdf", response_model=PDFProcessResult)
async def upload_pdf(file: UploadFile = File(...)):
    """Process PDF file and extract quote information automatically"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    try:
        # Read PDF content
        pdf_content = await file.read()
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_content)
        
        if not extracted_text:
            return PDFProcessResult(
                success=False,
                message="No se pudo extraer texto del PDF",
                quotes_created=0,
                errors=["PDF vacío o no se pudo procesar"]
            )
        
        # Parse quote data from text
        quote_data = parse_quote_from_text(extracted_text)
        
        # Validate required fields
        if not quote_data["procedure_name"]:
            return PDFProcessResult(
                success=False,
                message="Información insuficiente en el PDF",
                quotes_created=0,
                extracted_data=quote_data,
                errors=["No se pudo identificar el procedimiento"]
            )
            
        if quote_data["surgery_duration_hours"] == 0:
            return PDFProcessResult(
                success=False,
                message="Información insuficiente en el PDF",
                quotes_created=0,
                extracted_data=quote_data,
                errors=["No se pudo identificar la duración de la cirugía en horas"]
            )
        
        if not quote_data["anesthesia_type"]:
            quote_data["anesthesia_type"] = "Anestesia General"  # Default
        
        # Calculate total cost
        total_cost = (quote_data["facility_fee"] + 
                     quote_data["equipment_costs"] + 
                     quote_data["anesthesia_fee"] + 
                     quote_data["other_costs"])
        
        quote_data['total_cost'] = total_cost
        
        # Create Quote object
        quote_obj = Quote(**quote_data)
        
        # Save to database
        quote_mongo = prepare_for_mongo(quote_obj.dict())
        await db.quotes.insert_one(quote_mongo)
        
        return PDFProcessResult(
            success=True,
            message="Cotización creada exitosamente desde PDF",
            quotes_created=1,
            extracted_data=quote_data
        )
        
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return PDFProcessResult(
            success=False,
            message=f"Error procesando PDF: {str(e)}",
            quotes_created=0,
            errors=[str(e)]
        )

@api_router.post("/quotes", response_model=Quote)
async def create_quote(quote_data: QuoteCreate):
    # Calculate total cost
    total_cost = (quote_data.facility_fee + 
                 quote_data.equipment_costs + (quote_data.anesthesia_fee or 0) + 
                 (quote_data.other_costs or 0))
    
    quote_dict = quote_data.dict()
    quote_dict['total_cost'] = total_cost
    quote_obj = Quote(**quote_dict)
    
    # Prepare for MongoDB
    quote_mongo = prepare_for_mongo(quote_obj.dict())
    await db.quotes.insert_one(quote_mongo)
    
    return quote_obj

@api_router.get("/quotes", response_model=List[Quote])
async def get_quotes(procedure_name: Optional[str] = None, surgeon_name: Optional[str] = None):
    filter_query = {}
    if procedure_name:
        filter_query["procedure_name"] = {"$regex": procedure_name, "$options": "i"}
    if surgeon_name:
        filter_query["surgeon_name"] = {"$regex": surgeon_name, "$options": "i"}
    
    quotes = await db.quotes.find(filter_query).sort("created_at", -1).to_list(1000)
    parsed_quotes = [parse_from_mongo(quote) for quote in quotes]
    return [Quote(**quote) for quote in parsed_quotes]

@api_router.get("/quotes/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str):
    quote = await db.quotes.find_one({"id": quote_id})
    if not quote:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    parsed_quote = parse_from_mongo(quote)
    return Quote(**parsed_quote)

@api_router.put("/quotes/{quote_id}", response_model=Quote)
async def update_quote(quote_id: str, quote_data: QuoteCreate):
    # Calculate total cost
    total_cost = (quote_data.facility_fee + 
                 quote_data.equipment_costs + (quote_data.anesthesia_fee or 0) + 
                 (quote_data.other_costs or 0))
    
    quote_dict = quote_data.dict()
    quote_dict['total_cost'] = total_cost
    quote_dict['id'] = quote_id
    
    # Prepare for MongoDB
    quote_mongo = prepare_for_mongo(quote_dict)
    
    result = await db.quotes.replace_one({"id": quote_id}, quote_mongo)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    return Quote(**quote_dict)

@api_router.delete("/quotes/{quote_id}")
async def delete_quote(quote_id: str):
    result = await db.quotes.delete_one({"id": quote_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return {"message": "Cotización eliminada exitosamente"}

@api_router.get("/pricing-suggestions/{procedure_name}", response_model=PricingSuggestion)
async def get_pricing_suggestions(procedure_name: str):
    # Get historical quotes for this procedure
    pipeline = [
        {"$match": {"procedure_name": {"$regex": procedure_name, "$options": "i"}}},
        {"$group": {
            "_id": None,
            "avg_facility_fee": {"$avg": "$facility_fee"},
            "avg_equipment_costs": {"$avg": "$equipment_costs"},
            "avg_total_cost": {"$avg": "$total_cost"},
            "count": {"$sum": 1}
        }}
    ]
    
    result = await db.quotes.aggregate(pipeline).to_list(1)
    
    if not result:
        return PricingSuggestion(
            procedure_name=procedure_name,
            avg_facility_fee=0,
            avg_equipment_costs=0,
            avg_total_cost=0,
            quote_count=0,
            suggested_total=0
        )
    
    data = result[0]
    suggested_total = data['avg_total_cost'] if data['avg_total_cost'] else 0
    
    return PricingSuggestion(
        procedure_name=procedure_name,
        avg_facility_fee=round(data['avg_facility_fee'] if data['avg_facility_fee'] else 0, 2),
        avg_equipment_costs=round(data['avg_equipment_costs'] if data['avg_equipment_costs'] else 0, 2),
        avg_total_cost=round(data['avg_total_cost'] if data['avg_total_cost'] else 0, 2),
        quote_count=data['count'],
        suggested_total=round(suggested_total, 2)
    )

@api_router.get("/procedures")
async def get_procedures():
    """Get list of unique procedure names for filtering"""
    procedures = await db.quotes.distinct("procedure_name")
    return {"procedures": procedures}

@api_router.get("/surgeons")
async def get_surgeons():
    """Get list of unique surgeon names for filtering"""
    surgeons = await db.quotes.distinct("surgeon_name")
    return {"surgeons": surgeons}

@api_router.get("/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_quotes = await db.quotes.count_documents({})
    
    # Recent quotes
    recent_quotes = await db.quotes.find().sort("created_at", -1).limit(5).to_list(5)
    parsed_recent = [parse_from_mongo(quote) for quote in recent_quotes]
    
    # Top procedures
    top_procedures_pipeline = [
        {"$group": {"_id": "$procedure_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_procedures = await db.quotes.aggregate(top_procedures_pipeline).to_list(5)
    
    return {
        "total_quotes": total_quotes,
        "recent_quotes": [Quote(**quote) for quote in parsed_recent],
        "top_procedures": [{"name": proc["_id"], "count": proc["count"]} for proc in top_procedures]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()