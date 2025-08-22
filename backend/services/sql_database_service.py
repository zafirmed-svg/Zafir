from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.sql_models import Quote, SurgicalPackage, Procedure, Surgeon
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SQLDatabaseService:
    def __init__(self, session: Session):
        if session is None:
            raise ValueError("Session cannot be None")
        self.session = session
        
    def _handle_error(self, operation: str, error: Exception):
        logger.error(f"Error in {operation}: {str(error)}", exc_info=True)
        try:
            self.session.rollback()
        except Exception as e:
            logger.error(f"Error during rollback in {operation}: {str(e)}", exc_info=True)
        return []

    # Surgeon operations
    def get_surgeons(self, skip: int = 0, limit: int = 10) -> List[Surgeon]:
        try:
            return self.session.query(Surgeon).offset(skip).limit(limit).all()
        except Exception as e:
            return self._handle_error("get_surgeons", e)

    def get_surgeon(self, surgeon_id: int) -> Optional[Surgeon]:
        try:
            return self.session.query(Surgeon).filter(Surgeon.id == surgeon_id).first()
        except Exception as e:
            self._handle_error("get_surgeon", e)
            return None

    # Procedure operations
    def get_procedures(self, skip: int = 0, limit: int = 10) -> List[Procedure]:
        try:
            return self.session.query(Procedure).offset(skip).limit(limit).all()
        except Exception as e:
            return self._handle_error("get_procedures", e)

    def get_procedure(self, procedure_id: int) -> Optional[Procedure]:
        try:
            return self.session.query(Procedure).filter(Procedure.id == procedure_id).first()
        except Exception as e:
            self._handle_error("get_procedure", e)
            return None

    # Quote operations
    def get_quotes(self, skip: int = 0, limit: int = 10) -> List[Quote]:
        try:
            quotes = self.session.query(Quote).offset(skip).limit(limit).all()
            return [
                {
                    "id": quote.id,
                    "patient_id": quote.patient_id,
                    "patient_age": quote.patient_age,
                    "patient_phone": quote.patient_phone,
                    "patient_email": quote.patient_email,
                    "procedure_name": quote.procedure_name,
                    "procedure_code": quote.procedure_code,
                    "procedure_description": quote.procedure_description,
                    "surgeon_name": quote.surgeon_name,
                    "surgeon_specialty": quote.surgeon_specialty,
                    "facility_fee": float(quote.facility_fee) if quote.facility_fee else 0,
                    "equipment_costs": float(quote.equipment_costs) if quote.equipment_costs else 0,
                    "anesthesia_fee": float(quote.anesthesia_fee) if quote.anesthesia_fee else 0,
                    "other_costs": float(quote.other_costs) if quote.other_costs else 0,
                    "surgery_duration_hours": quote.surgery_duration_hours,
                    "created_by": quote.created_by,
                    "notes": quote.notes,
                    "surgical_package": quote.surgical_package,
                    "created_at": quote.created_at.isoformat() if quote.created_at else None,
                    "status": quote.status,
                    "total_cost": float(sum(x or 0 for x in [quote.facility_fee, quote.equipment_costs, quote.anesthesia_fee, quote.other_costs]))
                } for quote in quotes
            ]
        except Exception as e:
            return self._handle_error("get_quotes", e)

    def create_quote(self, quote_data: dict) -> Quote:
        try:
            # Convert numeric strings to appropriate types
            if quote_data.get('facility_fee'):
                quote_data['facility_fee'] = float(quote_data['facility_fee'])
            if quote_data.get('equipment_costs'):
                quote_data['equipment_costs'] = float(quote_data['equipment_costs'])
            if quote_data.get('anesthesia_fee'):
                quote_data['anesthesia_fee'] = float(quote_data['anesthesia_fee'])
            if quote_data.get('other_costs'):
                quote_data['other_costs'] = float(quote_data['other_costs'])
            if quote_data.get('surgery_duration_hours'):
                quote_data['surgery_duration_hours'] = int(quote_data['surgery_duration_hours'])

            # Create the quote
            quote = Quote(**quote_data)
            self.session.add(quote)
            self.session.commit()
            return quote
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Error creating quote: {str(e)}")

    # Dashboard statistics
    def get_pricing_suggestions(self, procedure_name: str) -> Dict[str, Any]:
        try:
            # Get quotes for similar procedures (case-insensitive LIKE search)
            similar_quotes = (
                self.session.query(Quote)
                .filter(func.lower(Quote.procedure_name).like(f"%{procedure_name.lower()}%"))
                .all()
            )
            
            if not similar_quotes:
                return {
                    "quote_count": 0,
                    "avg_facility_fee": 0,
                    "avg_equipment_costs": 0,
                    "avg_total_cost": 0
                }
                
            # Calculate averages
            total_count = len(similar_quotes)
            total_facility_fee = sum(quote.facility_fee for quote in similar_quotes if quote.facility_fee)
            total_equipment_costs = sum(quote.equipment_costs for quote in similar_quotes if quote.equipment_costs)
            total_costs = sum((quote.facility_fee or 0) + (quote.equipment_costs or 0) for quote in similar_quotes)
            
            return {
                "quote_count": total_count,
                "avg_facility_fee": total_facility_fee / total_count if total_count > 0 else 0,
                "avg_equipment_costs": total_equipment_costs / total_count if total_count > 0 else 0,
                "avg_total_cost": total_costs / total_count if total_count > 0 else 0
            }
        except Exception as e:
            print(f"Error in get_pricing_suggestions: {str(e)}")
            return {
                "quote_count": 0,
                "avg_facility_fee": 0,
                "avg_equipment_costs": 0,
                "avg_total_cost": 0
            }

    def get_dashboard_stats(self) -> Dict[str, Any]:
        try:
            total_quotes = self.session.query(func.count(Quote.id)).scalar() or 0
            total_procedures = self.session.query(func.count(Procedure.id)).scalar() or 0
            total_surgeons = self.session.query(func.count(Surgeon.id)).scalar() or 0
            total_packages = self.session.query(func.count(SurgicalPackage.id)).scalar() or 0

            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_quotes = (
                self.session.query(func.count(Quote.id))
                .filter(Quote.created_at >= yesterday)
                .scalar() or 0
            )

            # Get recent quotes
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_quotes = (
                self.session.query(Quote)
                .filter(Quote.created_at >= yesterday)
                .limit(5)
                .all()
            )
            
            # Get top procedures
            top_procedures = (
                self.session.query(
                    Quote.procedure_name.label('name'),
                    func.count(Quote.id).label('count')
                )
                .group_by(Quote.procedure_name)
                .order_by(func.count(Quote.id).desc())
                .limit(5)
                .all()
            )

            return {
                "total_quotes": total_quotes,
                "recent_quotes": [
                    {
                        "id": quote.id,
                        "patient_id": quote.patient_id,
                        "procedure_name": quote.procedure_name,
                        "surgery_duration_hours": quote.surgery_duration_hours,
                        "total_cost": float(sum(x or 0 for x in [quote.facility_fee, quote.equipment_costs, quote.anesthesia_fee, quote.other_costs])),
                        "created_at": quote.created_at.isoformat() if quote.created_at else None,
                        "status": quote.status
                    } for quote in recent_quotes
                ],
                "top_procedures": [
                    {"name": name, "count": count} for name, count in top_procedures
                ],
                "total_procedures": total_procedures,
                "total_surgeons": total_surgeons,
                "total_packages": total_packages
            }
        except Exception as e:
            print(f"Error in get_dashboard_stats: {str(e)}")
            return {
                "total_quotes": 0,
                "recent_quotes": [],
                "top_procedures": [],
                "total_procedures": 0,
                "total_surgeons": 0,
                "total_packages": 0
            }
