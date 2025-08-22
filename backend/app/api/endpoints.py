from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from ..models.quote import Quote, QuoteCreate, PricingSuggestion, PDFProcessResult
from ..services.database_service import DatabaseService
from ..services.pdf_service import extract_text_from_pdf, parse_quote_from_text
from ..core.config import settings

router = APIRouter(prefix="/api")
db_service = DatabaseService(settings.mongo_url, settings.db_name)

@router.get("/")
async def root():
    return {"message": "Sistema de Gestión de Cotizaciones Quirúrgicas"}

@router.post("/upload-pdf", response_model=PDFProcessResult)
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
        
        # Create Quote object and save
        quote_obj = Quote(**quote_data)
        await db_service.create_quote(quote_obj)
        
        return PDFProcessResult(
            success=True,
            message="Cotización creada exitosamente desde PDF",
            quotes_created=1,
            extracted_data=quote_data
        )
        
    except Exception as e:
        return PDFProcessResult(
            success=False,
            message=f"Error procesando PDF: {str(e)}",
            quotes_created=0,
            errors=[str(e)]
        )

@router.post("/quotes", response_model=Quote)
async def create_quote(quote_data: QuoteCreate):
    # Calculate total cost
    total_cost = (quote_data.facility_fee + 
                 quote_data.equipment_costs + (quote_data.anesthesia_fee or 0) + 
                 (quote_data.other_costs or 0))
    
    quote_dict = quote_data.dict()
    quote_dict['total_cost'] = total_cost
    quote_obj = Quote(**quote_dict)
    
    return await db_service.create_quote(quote_obj)

@router.get("/quotes", response_model=List[Quote])
async def get_quotes(procedure_name: Optional[str] = None, surgeon_name: Optional[str] = None):
    return await db_service.get_quotes(procedure_name, surgeon_name)

@router.get("/quotes/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str):
    quote = await db_service.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return quote

@router.put("/quotes/{quote_id}", response_model=Quote)
async def update_quote(quote_id: str, quote_data: QuoteCreate):
    # Calculate total cost
    total_cost = (quote_data.facility_fee + 
                 quote_data.equipment_costs + (quote_data.anesthesia_fee or 0) + 
                 (quote_data.other_costs or 0))
    
    quote_dict = quote_data.dict()
    quote_dict['total_cost'] = total_cost
    quote_dict['id'] = quote_id
    quote_obj = Quote(**quote_dict)
    
    updated_quote = await db_service.update_quote(quote_id, quote_obj)
    if not updated_quote:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return updated_quote

@router.delete("/quotes/{quote_id}")
async def delete_quote(quote_id: str):
    if not await db_service.delete_quote(quote_id):
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return {"message": "Cotización eliminada exitosamente"}

@router.get("/pricing-suggestions/{procedure_name}", response_model=PricingSuggestion)
async def get_pricing_suggestions(procedure_name: str):
    return await db_service.get_pricing_suggestions(procedure_name)

@router.get("/procedures")
async def get_procedures():
    """Get list of unique procedure names for filtering"""
    procedures = await db_service.get_unique_procedures()
    return {"procedures": procedures}

@router.get("/surgeons")
async def get_surgeons():
    """Get list of unique surgeon names for filtering"""
    surgeons = await db_service.get_unique_surgeons()
    return {"surgeons": surgeons}

@router.get("/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return await db_service.get_dashboard_stats()
