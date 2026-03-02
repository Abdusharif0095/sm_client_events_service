import json
from kafka import KafkaConsumer, KafkaProducer

from src.models import models
from lib.config import settings


def get_consumer(topic: str, group_id: str, auto_offset_reset: str, enable_auto_commit: bool):
    return KafkaConsumer(topic,
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset=auto_offset_reset,
                         enable_auto_commit=enable_auto_commit,
                         group_id=group_id,
                         value_deserializer=lambda x: x.decode('utf-8')
                        )


def get_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer


def send_client_event(user_id: str, request: models.EventModel):
    producer = get_kafka_producer()
    producer.send(settings.CLIENT_EVENTS_TOPIC, key=user_id.encode('utf-8'), value=request.__dict__)


def send_ping_response(ping_uuid: str, request: models.EventModel):
    producer = get_kafka_producer()
    producer.send(settings.PING_RESPONSES_TOPIC, key=ping_uuid.encode('utf-8'), value=request.__dict__)
