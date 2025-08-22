from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from ..models.quote import Quote, PricingSuggestion

class DatabaseService:
    def __init__(self, mongo_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]

    def prepare_for_mongo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        return data

    def parse_from_mongo(self, item: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(item.get('created_at'), str):
            item['created_at'] = datetime.fromisoformat(item['created_at'])
        return item

    async def create_quote(self, quote: Quote) -> Quote:
        quote_mongo = self.prepare_for_mongo(quote.dict())
        await self.db.quotes.insert_one(quote_mongo)
        return quote

    async def get_quotes(self, procedure_name: Optional[str] = None, surgeon_name: Optional[str] = None) -> List[Quote]:
        filter_query = {}
        if procedure_name:
            filter_query["procedure_name"] = {"$regex": procedure_name, "$options": "i"}
        if surgeon_name:
            filter_query["surgeon_name"] = {"$regex": surgeon_name, "$options": "i"}
        
        quotes = await self.db.quotes.find(filter_query).sort("created_at", -1).to_list(1000)
        parsed_quotes = [self.parse_from_mongo(quote) for quote in quotes]
        return [Quote(**quote) for quote in parsed_quotes]

    async def get_quote(self, quote_id: str) -> Optional[Quote]:
        quote = await self.db.quotes.find_one({"id": quote_id})
        if quote:
            parsed_quote = self.parse_from_mongo(quote)
            return Quote(**parsed_quote)
        return None

    async def update_quote(self, quote_id: str, quote: Quote) -> Optional[Quote]:
        quote_mongo = self.prepare_for_mongo(quote.dict())
        result = await self.db.quotes.replace_one({"id": quote_id}, quote_mongo)
        if result.matched_count > 0:
            return quote
        return None

    async def delete_quote(self, quote_id: str) -> bool:
        result = await self.db.quotes.delete_one({"id": quote_id})
        return result.deleted_count > 0

    async def get_pricing_suggestions(self, procedure_name: str) -> PricingSuggestion:
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
        
        result = await self.db.quotes.aggregate(pipeline).to_list(1)
        
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

    async def get_unique_procedures(self) -> List[str]:
        return await self.db.quotes.distinct("procedure_name")

    async def get_unique_surgeons(self) -> List[str]:
        return await self.db.quotes.distinct("surgeon_name")

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        total_quotes = await self.db.quotes.count_documents({})
        
        recent_quotes = await self.db.quotes.find().sort("created_at", -1).limit(5).to_list(5)
        parsed_recent = [self.parse_from_mongo(quote) for quote in recent_quotes]
        
        top_procedures_pipeline = [
            {"$group": {"_id": "$procedure_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_procedures = await self.db.quotes.aggregate(top_procedures_pipeline).to_list(5)
        
        return {
            "total_quotes": total_quotes,
            "recent_quotes": [Quote(**quote) for quote in parsed_recent],
            "top_procedures": [{"name": proc["_id"], "count": proc["count"]} for proc in top_procedures]
        }

    def close(self):
        self.client.close()
