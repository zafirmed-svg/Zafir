from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..models.quote import Quote as QuoteSchema, PricingSuggestion, SurgicalPackage as SurgicalPackageSchema
from ..models.sql_models import Quote as QuoteModel, SurgicalPackage as SurgicalPackageModel

class SQLDatabaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_schema(self, quote_model: QuoteModel) -> QuoteSchema:
        surgical_package = None
        if quote_model.surgical_package:
            surgical_package = SurgicalPackageSchema(
                medications_included=quote_model.surgical_package.medications_included or [],
                postoperative_care=quote_model.surgical_package.postoperative_care or [],
                hospital_stay_nights=quote_model.surgical_package.hospital_stay_nights or 0,
                special_equipment=quote_model.surgical_package.special_equipment or [],
                dietary_plan=quote_model.surgical_package.dietary_plan or False,
                additional_services=quote_model.surgical_package.additional_services or []
            )

        return QuoteSchema(
            id=quote_model.id,
            patient_id=quote_model.patient_id,
            patient_age=quote_model.patient_age,
            patient_phone=quote_model.patient_phone,
            patient_email=quote_model.patient_email,
            procedure_name=quote_model.procedure_name,
            procedure_code=quote_model.procedure_code,
            procedure_description=quote_model.procedure_description,
            surgeon_name=quote_model.surgeon_name,
            surgeon_specialty=quote_model.surgeon_specialty,
            surgery_duration_hours=quote_model.surgery_duration_hours,
            anesthesia_type=quote_model.anesthesia_type,
            additional_equipment=quote_model.additional_equipment,
            additional_materials=quote_model.additional_materials,
            is_ambulatory=quote_model.is_ambulatory,
            hospital_nights=quote_model.hospital_nights,
            facility_fee=quote_model.facility_fee,
            equipment_costs=quote_model.equipment_costs,
            anesthesia_fee=quote_model.anesthesia_fee,
            other_costs=quote_model.other_costs,
            total_cost=quote_model.total_cost,
            created_at=quote_model.created_at,
            created_by=quote_model.created_by,
            status=quote_model.status,
            notes=quote_model.notes,
            surgical_package=surgical_package
        )

    async def create_quote(self, quote: QuoteSchema) -> QuoteSchema:
        surgical_package = None
        if quote.surgical_package:
            surgical_package = SurgicalPackageModel(
                medications_included=quote.surgical_package.medications_included,
                postoperative_care=quote.surgical_package.postoperative_care,
                hospital_stay_nights=quote.surgical_package.hospital_stay_nights,
                special_equipment=quote.surgical_package.special_equipment,
                dietary_plan=quote.surgical_package.dietary_plan,
                additional_services=quote.surgical_package.additional_services
            )

        quote_model = QuoteModel(
            id=quote.id,
            patient_id=quote.patient_id,
            patient_age=quote.patient_age,
            patient_phone=quote.patient_phone,
            patient_email=quote.patient_email,
            procedure_name=quote.procedure_name,
            procedure_code=quote.procedure_code,
            procedure_description=quote.procedure_description,
            surgeon_name=quote.surgeon_name,
            surgeon_specialty=quote.surgeon_specialty,
            surgery_duration_hours=quote.surgery_duration_hours,
            anesthesia_type=quote.anesthesia_type,
            additional_equipment=quote.additional_equipment,
            additional_materials=quote.additional_materials,
            is_ambulatory=quote.is_ambulatory,
            hospital_nights=quote.hospital_nights,
            facility_fee=quote.facility_fee,
            equipment_costs=quote.equipment_costs,
            anesthesia_fee=quote.anesthesia_fee,
            other_costs=quote.other_costs,
            total_cost=quote.total_cost,
            created_by=quote.created_by,
            status=quote.status,
            notes=quote.notes,
            surgical_package=surgical_package
        )

        self.session.add(quote_model)
        await self.session.flush()
        await self.session.refresh(quote_model)
        return self._model_to_schema(quote_model)

    async def get_quotes(self, procedure_name: Optional[str] = None, surgeon_name: Optional[str] = None) -> List[QuoteSchema]:
        query = select(QuoteModel).options(selectinload(QuoteModel.surgical_package))
        
        if procedure_name:
            query = query.where(QuoteModel.procedure_name.ilike(f"%{procedure_name}%"))
        if surgeon_name:
            query = query.where(QuoteModel.surgeon_name.ilike(f"%{surgeon_name}%"))
        
        query = query.order_by(QuoteModel.created_at.desc())
        result = await self.session.execute(query)
        quotes = result.scalars().all()
        return [self._model_to_schema(quote) for quote in quotes]

    async def get_quote(self, quote_id: str) -> Optional[QuoteSchema]:
        query = select(QuoteModel).options(selectinload(QuoteModel.surgical_package)).where(QuoteModel.id == quote_id)
        result = await self.session.execute(query)
        quote = result.scalar_one_or_none()
        return self._model_to_schema(quote) if quote else None

    async def update_quote(self, quote_id: str, quote: QuoteSchema) -> Optional[QuoteSchema]:
        db_quote = await self.get_quote(quote_id)
        if not db_quote:
            return None

        quote_data = quote.dict(exclude_unset=True)
        
        query = select(QuoteModel).options(selectinload(QuoteModel.surgical_package)).where(QuoteModel.id == quote_id)
        result = await self.session.execute(query)
        quote_model = result.scalar_one()

        for field, value in quote_data.items():
            if field != "surgical_package":
                setattr(quote_model, field, value)
            else:
                if value:
                    if quote_model.surgical_package:
                        for sp_field, sp_value in value.items():
                            setattr(quote_model.surgical_package, sp_field, sp_value)
                    else:
                        quote_model.surgical_package = SurgicalPackageModel(**value)

        await self.session.flush()
        await self.session.refresh(quote_model)
        return self._model_to_schema(quote_model)

    async def delete_quote(self, quote_id: str) -> bool:
        query = select(QuoteModel).where(QuoteModel.id == quote_id)
        result = await self.session.execute(query)
        quote = result.scalar_one_or_none()
        if quote:
            await self.session.delete(quote)
            return True
        return False

    async def get_pricing_suggestions(self, procedure_name: str) -> PricingSuggestion:
        query = select(
            func.avg(QuoteModel.facility_fee).label('avg_facility_fee'),
            func.avg(QuoteModel.equipment_costs).label('avg_equipment_costs'),
            func.avg(QuoteModel.total_cost).label('avg_total_cost'),
            func.count().label('count')
        ).where(QuoteModel.procedure_name.ilike(f"%{procedure_name}%"))

        result = await self.session.execute(query)
        data = result.first()

        if not data or not data.count:
            return PricingSuggestion(
                procedure_name=procedure_name,
                avg_facility_fee=0,
                avg_equipment_costs=0,
                avg_total_cost=0,
                quote_count=0,
                suggested_total=0
            )

        return PricingSuggestion(
            procedure_name=procedure_name,
            avg_facility_fee=round(data.avg_facility_fee or 0, 2),
            avg_equipment_costs=round(data.avg_equipment_costs or 0, 2),
            avg_total_cost=round(data.avg_total_cost or 0, 2),
            quote_count=data.count,
            suggested_total=round(data.avg_total_cost or 0, 2)
        )

    async def get_unique_procedures(self) -> List[str]:
        query = select(QuoteModel.procedure_name).distinct()
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]

    async def get_unique_surgeons(self) -> List[str]:
        query = select(QuoteModel.surgeon_name).distinct().where(QuoteModel.surgeon_name.isnot(None))
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        # Total quotes
        total_query = select(func.count()).select_from(QuoteModel)
        total_result = await self.session.execute(total_query)
        total_quotes = total_result.scalar()

        # Recent quotes
        recent_query = select(QuoteModel).options(selectinload(QuoteModel.surgical_package)).order_by(QuoteModel.created_at.desc()).limit(5)
        recent_result = await self.session.execute(recent_query)
        recent_quotes = recent_result.scalars().all()

        # Top procedures
        top_proc_query = select(
            QuoteModel.procedure_name,
            func.count().label('count')
        ).group_by(QuoteModel.procedure_name).order_by(func.count().desc()).limit(5)
        top_proc_result = await self.session.execute(top_proc_query)
        top_procedures = [{"name": name, "count": count} for name, count in top_proc_result.fetchall()]

        return {
            "total_quotes": total_quotes,
            "recent_quotes": [self._model_to_schema(quote) for quote in recent_quotes],
            "top_procedures": top_procedures
        }

    async def close(self):
        await self.session.close()
