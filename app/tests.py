from app import app
import unittest
import json


class APITestCase(unittest.TestCase):

	def test_healthcheck(self):
		with app.test_client() as client:
			response = client.get('/healthcheck')
		self.assertEqual(response.status_code, 200)

	def test_load(self):
		with app.test_client() as client:
			response = client.get('/load/TEST_SESSION')
		self.assertEqual(response.status_code, 200)

	def test_interview(self):
		with app.test_client() as client:
			r = client.get('/STOCK_MARKET/TEST_SESSION')
			self.assertEqual(r.status_code, 200)
			response = client.post('/next', 
				data=json.dumps({
					"user_message": "I can't afford it and the stock market is rigged.",
					"interview_id": "STOCK_MARKET",
					"session_id": "TEST_SESSION"
				}), 
				content_type='application/json'
			)
		self.assertEqual(response.status_code, 200)
		body = json.loads(response.data)
		self.assertIsInstance(body, dict)
		self.assertIn('message', body)
		self.assertIsInstance(body['message'], str)
		print(f"\nReceived 'next' response: {body['message']}\n")

	def test_delete(self):
		with app.test_client() as client:
			response = client.get('/delete/TEST_SESSION')
		self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
	unittest.main()
