import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, engine
from models.sql_models import Surgeon, Procedure, Base
from datetime import datetime

def seed_database():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear una sesión
    db = SessionLocal()
    try:
        # Crear cirujanos de prueba
        surgeons = [
            Surgeon(
                name="Dr. Juan Pérez",
                specialty="Cirugía General",
                license_number="12345",
                contact_info={"email": "juan.perez@example.com", "phone": "123-456-7890"},
                created_at=datetime.utcnow()
            ),
            Surgeon(
                name="Dra. María García",
                specialty="Cirugía Cardíaca",
                license_number="67890",
                contact_info={"email": "maria.garcia@example.com", "phone": "098-765-4321"},
                created_at=datetime.utcnow()
            )
        ]
        
        # Crear procedimientos de prueba
        procedures = [
            Procedure(
                name="Apendicectomía",
                description="Extirpación del apéndice",
                estimated_time=60,  # minutos
                price=1500.00,
                created_at=datetime.utcnow()
            ),
            Procedure(
                name="Bypass Coronario",
                description="Cirugía de derivación coronaria",
                estimated_time=240,  # minutos
                price=15000.00,
                created_at=datetime.utcnow()
            )
        ]

        # Agregar datos a la base de datos
        db.add_all(surgeons)
        db.add_all(procedures)
        db.commit()
        print("Datos de prueba agregados exitosamente")
        
    except Exception as e:
        print(f"Error al agregar datos de prueba: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
