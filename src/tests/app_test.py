import unittest
from app import app, storage, warehouses


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        storage.clear()

    def test_index_empty(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No warehouses yet', response.data)

    def test_create_warehouse_page(self):
        response = self.client.get('/warehouse/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Warehouse', response.data)

    def test_create_warehouse(self):
        response = self.client.post('/warehouse/create', data={
            'name': 'Test Warehouse',
            'tilavuus': '100',
            'alku_saldo': '50'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)

    def test_create_warehouse_without_name(self):
        response = self.client.post('/warehouse/create', data={
            'name': '',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name required', response.data)

    def test_view_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'View Test',
            'tilavuus': '100',
            'alku_saldo': '25'
        })
        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View Test', response.data)
        self.assertIn(b'25', response.data)

    def test_view_nonexistent_warehouse(self):
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Warehouses', response.data)

    def test_edit_warehouse_page(self):
        self.client.post('/warehouse/create', data={
            'name': 'Edit Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Warehouse', response.data)

    def test_edit_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Original Name',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': 'New Name',
            'tilavuus': '200'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Name', response.data)
        self.assertEqual(warehouses[1]['varasto'].tilavuus, 200)

    def test_add_to_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Add Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.client.post('/warehouse/1/add', data={'maara': '50'})
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 50)

    def test_remove_from_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Remove Test',
            'tilavuus': '100',
            'alku_saldo': '75'
        })
        self.client.post('/warehouse/1/remove', data={'maara': '25'})
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 50)

    def test_delete_warehouse(self):
        self.client.post('/warehouse/create', data={
            'name': 'Delete Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        self.assertEqual(len(warehouses), 1)
        response = self.client.post(
            '/warehouse/1/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_create_warehouse_invalid_values(self):
        response = self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': 'invalid',
            'alku_saldo': '0'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid values', response.data)

    def test_edit_warehouse_invalid_capacity(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': 'Test',
            'tilavuus': 'invalid'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid capacity', response.data)

    def test_edit_warehouse_without_name(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post('/warehouse/1/edit', data={
            'name': '',
            'tilavuus': '100'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name required', response.data)

    def test_edit_nonexistent_warehouse(self):
        response = self.client.get('/warehouse/999/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_to_nonexistent_warehouse(self):
        response = self.client.post(
            '/warehouse/999/add',
            data={'maara': '10'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_from_nonexistent_warehouse(self):
        response = self.client.post(
            '/warehouse/999/remove',
            data={'maara': '10'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_add_invalid_amount(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '0'
        })
        response = self.client.post(
            '/warehouse/1/add',
            data={'maara': 'invalid'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 0)

    def test_remove_invalid_amount(self):
        self.client.post('/warehouse/create', data={
            'name': 'Test',
            'tilavuus': '100',
            'alku_saldo': '50'
        })
        response = self.client.post(
            '/warehouse/1/remove',
            data={'maara': 'invalid'},
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 50)


class TestFlaskApiEndpoints(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        storage.clear()

    def test_api_create_warehouse(self):
        response = self.client.post('/api/warehouse',
            json={'name': 'API Test', 'tilavuus': 100, 'alku_saldo': 25})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'API Test')
        self.assertEqual(data['tilavuus'], 100)
        self.assertEqual(data['saldo'], 25)

    def test_api_create_warehouse_no_name(self):
        response = self.client.post('/api/warehouse',
            json={'name': '', 'tilavuus': 100})
        self.assertEqual(response.status_code, 400)

    def test_api_update_warehouse(self):
        self.client.post('/api/warehouse',
            json={'name': 'Original', 'tilavuus': 100, 'alku_saldo': 0})
        response = self.client.put('/api/warehouse/1',
            json={'name': 'Updated', 'tilavuus': 200})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Updated')
        self.assertEqual(data['tilavuus'], 200)

    def test_api_update_nonexistent(self):
        response = self.client.put('/api/warehouse/999',
            json={'name': 'Test', 'tilavuus': 100})
        self.assertEqual(response.status_code, 404)

    def test_api_delete_warehouse(self):
        self.client.post('/api/warehouse',
            json={'name': 'Delete Me', 'tilavuus': 100})
        response = self.client.delete('/api/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_api_delete_nonexistent(self):
        response = self.client.delete('/api/warehouse/999')
        self.assertEqual(response.status_code, 404)

    def test_api_add_content(self):
        self.client.post('/api/warehouse',
            json={'name': 'Add Test', 'tilavuus': 100, 'alku_saldo': 0})
        response = self.client.post('/api/warehouse/1/add',
            json={'maara': 50})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['saldo'], 50)
        self.assertEqual(data['added'], 50)

    def test_api_remove_content(self):
        self.client.post('/api/warehouse',
            json={'name': 'Remove Test', 'tilavuus': 100, 'alku_saldo': 75})
        response = self.client.post('/api/warehouse/1/remove',
            json={'maara': 25})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['saldo'], 50)
        self.assertEqual(data['removed'], 25)

    def test_api_add_nonexistent_warehouse(self):
        response = self.client.post('/api/warehouse/999/add',
            json={'maara': 10})
        self.assertEqual(response.status_code, 404)

    def test_api_remove_nonexistent_warehouse(self):
        response = self.client.post('/api/warehouse/999/remove',
            json={'maara': 10})
        self.assertEqual(response.status_code, 404)
