from locust import HttpUser, task, between
from random import randint, choice
from time import sleep
from json.decoder import JSONDecodeError

sample_messages = [
	"I dont like stocks nor do I trust them",
	"The game is rigged, only the big funds profit while the rest of us will inevitable lose",
	"They have all the access, all the hardware to trade quickly, and all the inside information",
	"In any case, I don't have enough money to lose. If the market swings and I lose what I have I won't be able to afford necessities",
	"I'd rather have safe funds saved away for rainy days",
	"My uncle Joe lost pretty much everything he had during the financial crash of '08. We learned our lesson then",
	"It's not even risk aversion, I am simply not interested in playing a losing game",
	"The costs of trading at our budget are too high",
	"If there were easier, more accessible tools to begin investing I think that would help",
	"In the future given more disposable, discretionary income I would like to put some money into the stock market"
]

class Quickstart(HttpUser):
	wait_time = between(0, 2)

	@task
	def test_interview(self):
		session_id = str(randint(1,100))
		interview_id = choice(["STOCK_MARKET", "VOTING"])
		
		# Load session
		r = self.client.get(f"/load/{session_id}")
		if r.status_code != 200 or not isinstance(r.json(), dict): 
			print(f"ERROR {r.status_code}: /load/{session_id} returned: {r.text}")
			return

		# Start session if not already started
		if not r.json():
			r = self.client.get(f"/{interview_id}/{session_id}")
			if r.status_code != 200:
				print(f"ERROR {r.status_code}: /{interview_id}/{session_id} returned: {r.text}")
				return
			sleep(1)

		# Continue session
		r = self.client.post("/next", json={
			"session_id": session_id,
			"interview_id": interview_id,
			"user_message": choice(sample_messages)
		})
		if r.status_code != 200:
			print(f"ERROR {r.status_code}: /next/{session_id} returned: {r.text}")
			return 
		try:
			message = r.json()['message']
			assert message
		except JSONDecodeError:
			print(f"ERROR {r.status_code}: /next/{session_id} returned empty: {r.text}")
			return 

		if 'unusual input' in message or 'interview is over' in message:
			# Delete session
			r = self.client.get(f"/delete/{session_id}")
			if r.status_code != 200:
				print(f"ERROR {r.status_code}: /delete/{session_id} returned: {r.text}")


### Run using e.g. ###
# locust -f locust.py --host=0.0.0.0:8000 --users=64 --spawn-rate=4 --html=report.html --run-time=240s
