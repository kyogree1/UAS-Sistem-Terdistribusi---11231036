import requests, os, json, time
from generator import make_event

TARGET = os.getenv("TARGET_URL", "http://aggregator:8080/publish")

while True:
    batch = {"events": [make_event() for _ in range(10)]}
    r = requests.post(TARGET, json=batch)
    print("Publish:", r.status_code, r.text)
    time.sleep(1)
