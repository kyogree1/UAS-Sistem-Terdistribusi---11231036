import uuid, random, time
from datetime import datetime

def make_event(topic="orders"):
    event_id = str(uuid.uuid4()) if random.random() > 0.3 else "dup-" + str(random.randint(1,50))
    return {
        "topic": topic,
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "publisher",
        "payload": {"value": random.randint(1,100)}
    }
