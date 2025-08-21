import requests
import sys
import json
from datetime import datetime, date

class SurgicalQuotesAPITester:
    def __init__(self, base_url="https://surgery-quotes.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_quote_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if method == 'POST' and 'id' in response_data:
                        self.created_quote_ids.append(response_data['id'])
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_create_quote(self, quote_data):
        """Test creating a quote"""
        return self.run_test("Create Quote", "POST", "quotes", 200, data=quote_data)

    def test_get_quotes(self):
        """Test getting all quotes"""
        return self.run_test("Get All Quotes", "GET", "quotes", 200)

    def test_get_quote_by_id(self, quote_id):
        """Test getting a specific quote"""
        return self.run_test("Get Quote by ID", "GET", f"quotes/{quote_id}", 200)

    def test_update_quote(self, quote_id, quote_data):
        """Test updating a quote"""
        return self.run_test("Update Quote", "PUT", f"quotes/{quote_id}", 200, data=quote_data)

    def test_delete_quote(self, quote_id):
        """Test deleting a quote"""
        return self.run_test("Delete Quote", "DELETE", f"quotes/{quote_id}", 200)

    def test_pricing_suggestions(self, procedure_name):
        """Test getting pricing suggestions"""
        return self.run_test("Get Pricing Suggestions", "GET", f"pricing-suggestions/{procedure_name}", 200)

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        return self.run_test("Get Dashboard Stats", "GET", "dashboard", 200)

    def test_get_procedures(self):
        """Test getting procedures list"""
        return self.run_test("Get Procedures", "GET", "procedures", 200)

    def test_get_surgeons(self):
        """Test getting surgeons list"""
        return self.run_test("Get Surgeons", "GET", "surgeons", 200)

    def test_surgical_package_validation(self, quote_id):
        """Test that surgical package data is properly stored and retrieved"""
        success, response = self.run_test("Validate Surgical Package Data", "GET", f"quotes/{quote_id}", 200)
        if success and 'surgical_package' in response:
            package = response['surgical_package']
            print(f"   📦 Surgical Package Details:")
            print(f"      - Preoperative tests: {len(package.get('preoperative_tests', []))} items")
            print(f"      - Medications: {len(package.get('medications_included', []))} items")
            print(f"      - Hospital stay: {package.get('hospital_stay_nights', 0)} nights")
            print(f"      - Follow-up consultations: {package.get('followup_consultations', 0)}")
            print(f"      - Physiotherapy sessions: {package.get('physiotherapy_sessions', 0)}")
            print(f"      - Dietary plan: {package.get('dietary_plan', False)}")
            return True, response
        return False, {}

    def test_search_quotes(self, procedure_name=None, surgeon_name=None):
        """Test searching quotes with filters"""
        params = {}
        if procedure_name:
            params['procedure_name'] = procedure_name
        if surgeon_name:
            params['surgeon_name'] = surgeon_name
        
        test_name = "Search Quotes"
        if procedure_name:
            test_name += f" by Procedure: {procedure_name}"
        if surgeon_name:
            test_name += f" by Surgeon: {surgeon_name}"
            
        return self.run_test(test_name, "GET", "quotes", 200, params=params)

def main():
    print("🏥 Starting Surgical Quotes Management System API Tests")
    print("=" * 60)
    
    tester = SurgicalQuotesAPITester()
    
    # Test 1: Root endpoint
    success, _ = tester.test_root_endpoint()
    if not success:
        print("❌ Root endpoint failed, stopping tests")
        return 1

    # Test 2: Dashboard stats (should work even with empty database)
    tester.test_dashboard_stats()

    # Test 3: Get procedures and surgeons (should work even if empty)
    tester.test_get_procedures()
    tester.test_get_surgeons()

    # Test 4: Get all quotes (should work even if empty)
    tester.test_get_quotes()

    # Test 5: Create sample quotes for testing (including Spanish procedures and surgical packages)
    sample_quotes = [
        {
            "patient_name": "Juan Pérez",
            "patient_id": "P001",
            "patient_age": 45,
            "patient_phone": "555-0123",
            "patient_email": "juan.perez@email.com",
            "procedure_name": "Reemplazo de Rodilla",
            "procedure_code": "RR001",
            "procedure_description": "Cirugía de reemplazo total de rodilla",
            "surgeon_name": "Dr. García",
            "surgeon_specialty": "Cirugía Ortopédica",
            "surgeon_fee": 5000.00,
            "facility_fee": 8000.00,
            "equipment_costs": 2000.00,
            "anesthesia_fee": 1500.00,
            "other_costs": 500.00,
            "scheduled_date": "2024-09-15",
            "estimated_duration": "02:30:00",
            "created_by": "Administrador de Prueba",
            "notes": "Paciente con diabetes, requiere monitoreo especial",
            "surgical_package": {
                "preoperative_tests": ["Análisis de sangre", "ECG", "Radiografía"],
                "medications_included": ["Antibióticos", "Analgésicos"],
                "postoperative_care": ["Curaciones", "Controles", "Retiro de puntos"],
                "hospital_stay_nights": 2,
                "followup_consultations": 3,
                "physiotherapy_sessions": 10,
                "special_equipment": ["Prótesis de rodilla", "Dispositivos de fijación"],
                "dietary_plan": True,
                "nursing_care_hours": 24,
                "additional_services": ["Transporte", "Acompañante"]
            }
        },
        {
            "patient_name": "María González",
            "patient_id": "P002",
            "patient_age": 62,
            "patient_phone": "555-0456",
            "patient_email": "maria.gonzalez@email.com",
            "procedure_name": "Cirugía de Bypass Cardíaco",
            "procedure_code": "CBC001",
            "procedure_description": "Cirugía de bypass de arteria coronaria",
            "surgeon_name": "Dr. Rodríguez",
            "surgeon_specialty": "Cirugía Cardíaca",
            "surgeon_fee": 12000.00,
            "facility_fee": 15000.00,
            "equipment_costs": 5000.00,
            "anesthesia_fee": 3000.00,
            "other_costs": 1000.00,
            "scheduled_date": "2024-09-20",
            "estimated_duration": "04:00:00",
            "created_by": "Administrador de Prueba",
            "notes": "Paciente de alto riesgo, requiere UCI post-operatoria",
            "surgical_package": {
                "preoperative_tests": ["Análisis completo de sangre", "Ecocardiograma", "Cateterismo"],
                "medications_included": ["Anticoagulantes", "Betabloqueadores", "Estatinas"],
                "postoperative_care": ["Monitoreo cardíaco", "Cuidados intensivos", "Rehabilitación cardíaca"],
                "hospital_stay_nights": 7,
                "followup_consultations": 5,
                "physiotherapy_sessions": 0,
                "special_equipment": ["Stents", "Dispositivos de monitoreo"],
                "dietary_plan": True,
                "nursing_care_hours": 168,
                "additional_services": ["Consulta nutricional", "Apoyo psicológico"]
            }
        },
        {
            "patient_name": "Carlos Martínez",
            "patient_id": "P003",
            "patient_age": 35,
            "patient_phone": "555-0789",
            "patient_email": "carlos.martinez@email.com",
            "procedure_name": "Apendicectomía",
            "procedure_code": "AP001",
            "procedure_description": "Apendicectomía laparoscópica",
            "surgeon_name": "Dr. López",
            "surgeon_specialty": "Cirugía General",
            "surgeon_fee": 3000.00,
            "facility_fee": 4000.00,
            "equipment_costs": 1000.00,
            "anesthesia_fee": 800.00,
            "other_costs": 200.00,
            "scheduled_date": "2024-09-10",
            "estimated_duration": "01:00:00",
            "created_by": "Administrador de Prueba",
            "notes": "Procedimiento de emergencia",
            "surgical_package": {
                "preoperative_tests": ["Análisis de sangre básico", "Ultrasonido abdominal"],
                "medications_included": ["Antibióticos profilácticos", "Analgésicos"],
                "postoperative_care": ["Observación", "Control de herida"],
                "hospital_stay_nights": 1,
                "followup_consultations": 1,
                "physiotherapy_sessions": 0,
                "special_equipment": [],
                "dietary_plan": False,
                "nursing_care_hours": 12,
                "additional_services": []
            }
        },
        {
            "patient_name": "Ana Fernández",
            "patient_id": "P004",
            "patient_age": 50,
            "patient_phone": "555-0321",
            "patient_email": "ana.fernandez@email.com",
            "procedure_name": "Reemplazo de Rodilla",
            "procedure_code": "RR002",
            "procedure_description": "Reemplazo parcial de rodilla",
            "surgeon_name": "Dr. García",
            "surgeon_specialty": "Cirugía Ortopédica",
            "surgeon_fee": 4500.00,
            "facility_fee": 7500.00,
            "equipment_costs": 1800.00,
            "anesthesia_fee": 1200.00,
            "other_costs": 300.00,
            "scheduled_date": "2024-09-25",
            "estimated_duration": "02:00:00",
            "created_by": "Administrador de Prueba",
            "notes": "Procedimiento de seguimiento",
            "surgical_package": {
                "preoperative_tests": ["Análisis de sangre", "Radiografía de rodilla"],
                "medications_included": ["Antibióticos", "Antiinflamatorios"],
                "postoperative_care": ["Fisioterapia temprana", "Control de dolor"],
                "hospital_stay_nights": 1,
                "followup_consultations": 2,
                "physiotherapy_sessions": 8,
                "special_equipment": ["Prótesis parcial"],
                "dietary_plan": False,
                "nursing_care_hours": 16,
                "additional_services": ["Equipo de rehabilitación"]
            }
        }
    ]

    print(f"\n📝 Creating {len(sample_quotes)} sample quotes...")
    created_quotes = []
    for i, quote_data in enumerate(sample_quotes):
        success, response = tester.test_create_quote(quote_data)
        if success:
            created_quotes.append(response)
            print(f"   ✅ Created quote {i+1}: {quote_data['patient_name']} - {quote_data['procedure_name']}")
        else:
            print(f"   ❌ Failed to create quote {i+1}")

    # Test 6: Get quotes after creation
    print(f"\n📋 Testing quote retrieval...")
    success, quotes_response = tester.test_get_quotes()
    if success:
        print(f"   ✅ Retrieved {len(quotes_response)} quotes")

    # Test 7: Test individual quote retrieval and surgical package validation
    if tester.created_quote_ids:
        tester.test_get_quote_by_id(tester.created_quote_ids[0])
        # Test surgical package data validation
        print(f"\n📦 Testing surgical package data validation...")
        tester.test_surgical_package_validation(tester.created_quote_ids[0])

    # Test 8: Test pricing suggestions (should have data now)
    print(f"\n💰 Testing pricing suggestions...")
    tester.test_pricing_suggestions("Reemplazo de Rodilla")
    tester.test_pricing_suggestions("Cirugía de Bypass Cardíaco")
    tester.test_pricing_suggestions("Apendicectomía")
    tester.test_pricing_suggestions("ProcedimientoInexistente")  # Should return empty data

    # Test 9: Test search functionality
    print(f"\n🔍 Testing search functionality...")
    tester.test_search_quotes(procedure_name="Reemplazo")
    tester.test_search_quotes(surgeon_name="García")
    tester.test_search_quotes(procedure_name="Bypass", surgeon_name="Rodríguez")

    # Test 10: Test update functionality
    if tester.created_quote_ids:
        print(f"\n✏️ Testing quote update...")
        update_data = sample_quotes[0].copy()
        update_data['patient_name'] = "Juan Pérez Actualizado"
        update_data['notes'] = "Notas actualizadas para prueba"
        # Update surgical package
        update_data['surgical_package']['physiotherapy_sessions'] = 15
        update_data['surgical_package']['additional_services'] = ["Transporte", "Acompañante", "Servicio especial"]
        tester.test_update_quote(tester.created_quote_ids[0], update_data)

    # Test 11: Dashboard stats after data creation
    print(f"\n📊 Testing dashboard with data...")
    success, dashboard_data = tester.test_dashboard_stats()
    if success:
        print(f"   ✅ Dashboard shows {dashboard_data.get('total_quotes', 0)} total quotes")
        print(f"   ✅ Recent quotes: {len(dashboard_data.get('recent_quotes', []))}")
        print(f"   ✅ Top procedures: {len(dashboard_data.get('top_procedures', []))}")

    # Test 12: Test procedures and surgeons lists (should have data now)
    print(f"\n📝 Testing lists after data creation...")
    success, procedures_data = tester.test_get_procedures()
    if success:
        procedures = procedures_data.get('procedures', [])
        print(f"   ✅ Found {len(procedures)} unique procedures: {procedures}")

    success, surgeons_data = tester.test_get_surgeons()
    if success:
        surgeons = surgeons_data.get('surgeons', [])
        print(f"   ✅ Found {len(surgeons)} unique surgeons: {surgeons}")

    # Test 13: Test delete functionality (clean up one quote)
    if tester.created_quote_ids:
        print(f"\n🗑️ Testing quote deletion...")
        tester.test_delete_quote(tester.created_quote_ids[-1])  # Delete last created quote

    # Print final results
    print(f"\n" + "=" * 60)
    print(f"📊 FINAL TEST RESULTS")
    print(f"=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print(f"🎉 ALL TESTS PASSED! Backend API is working correctly.")
        return 0
    else:
        print(f"⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())