from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class QuotesAPITest(APITestCase):
    def test_create_quote(self):
        url = '/api/quotes/create/'
        payload = {
            'procedure_name': 'Unit Test Procedure',
            'surgery_duration_hours': 1,
            'anesthesia_type': 'Local',
            'facility_fee': 500.0,
            'equipment_costs': 50.0,
            'anesthesia_fee': 20.0,
            'other_costs': 0.0,
            'created_by': 'unit_test',
            'notes': 'Created by unit test'
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', resp.data)
        self.assertEqual(resp.data['procedure_name'], payload['procedure_name'])

    def test_list_quotes(self):
        # create one quote first
        create_url = '/api/quotes/create/'
        payload = {
            'procedure_name': 'List Test Procedure',
            'surgery_duration_hours': 2,
            'anesthesia_type': 'General',
            'facility_fee': 800.0,
            'equipment_costs': 150.0,
            'anesthesia_fee': 100.0,
            'other_costs': 0.0,
            'created_by': 'unit_test',
            'notes': 'Created by unit test for list'
        }
        resp = self.client.post(create_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        list_url = '/api/quotes/'
        resp2 = self.client.get(list_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp2.data, list)
        # ensure at least one quote exists and matches
        self.assertTrue(any(q['procedure_name'] == payload['procedure_name'] for q in resp2.data))

    def test_update_and_delete_quote(self):
        # create
        url = '/api/quotes/create/'
        payload = {
            'procedure_name': 'Update Test',
            'surgery_duration_hours': 3,
            'facility_fee': 700.0,
            'equipment_costs': 100.0,
            'anesthesia_fee': 50.0,
            'other_costs': 0.0,
            'created_by': 'unit_test'
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        quote_id = resp.data['id']

        # update
        update_url = f'/api/quotes/{quote_id}/update/'
        new_data = {'facility_fee': 900.0, 'equipment_costs': 120.0}
        resp2 = self.client.put(update_url, new_data, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(float(resp2.data['facility_fee']), 900.0)

        # delete
        del_url = f'/api/quotes/{quote_id}/delete/'
        resp3 = self.client.delete(del_url)
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)

        # ensure it's gone
        list_url = '/api/quotes/'
        resp4 = self.client.get(list_url)
        self.assertEqual(resp4.status_code, status.HTTP_200_OK)
        self.assertFalse(any(q['id'] == quote_id for q in resp4.data))

    def test_pricing_suggestions_and_lists(self):
        # create two quotes for same procedure with different costs
        base = '/api/quotes/create/'
        p1 = {'procedure_name': 'PricingProc', 'surgery_duration_hours': 1, 'facility_fee': 100.0, 'equipment_costs': 10.0, 'anesthesia_fee': 5.0, 'other_costs': 0.0}
        p2 = {'procedure_name': 'PricingProc', 'surgery_duration_hours': 2, 'facility_fee': 200.0, 'equipment_costs': 20.0, 'anesthesia_fee': 10.0, 'other_costs': 0.0}
        self.client.post(base, p1, format='json')
        self.client.post(base, p2, format='json')

        ps_url = '/api/pricing-suggestions/PricingProc/'
        resp = self.client.get(ps_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('avg_total_cost', resp.data)
        self.assertGreaterEqual(resp.data['quote_count'], 2)

        # procedures list
        proc_url = '/api/procedures/'
        r2 = self.client.get(proc_url)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertIn('PricingProc', r2.data.get('procedures', []))

        # surgeons list (none set yet)
        surg_url = '/api/surgeons/'
        r3 = self.client.get(surg_url)
        self.assertEqual(r3.status_code, status.HTTP_200_OK)

    def test_dashboard_summary(self):
        # create a couple of quotes
        base = '/api/quotes/create/'
        for i in range(3):
            self.client.post(base, {'procedure_name': f'DashProc{i}', 'surgery_duration_hours': 1, 'facility_fee': 100.0 + i, 'equipment_costs': 10.0, 'anesthesia_fee': 5.0, 'other_costs': 0.0}, format='json')

        dash_url = '/api/dashboard/'
        resp = self.client.get(dash_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('total_quotes', resp.data)
        self.assertGreaterEqual(resp.data['total_quotes'], 3)
