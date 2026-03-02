from kafka import KafkaProducer
import json
from src.models import models

def get_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer

def send_client_event(user_id: str, request: models.EventModel):
    producer = get_kafka_producer()
    producer.send('client_events_topic', key=user_id.encode('utf-8'), value=request.__dict__)