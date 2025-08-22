import pdfplumber
import io
import re
import logging
from typing import Dict, Any

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

def parse_quote_from_text(text: str) -> Dict[str, Any]:
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
    
    # Surgeon name patterns
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
    
    # Duration patterns
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
