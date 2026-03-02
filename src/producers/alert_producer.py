import json
from aiokafka import AIOKafkaProducer
from lib.config import settings
from src.models.models import Alert


class AlertProducer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_alert(self, alert: Alert):
        await self.producer.send_and_wait(
            settings.ALERTS_TOPIC,
            alert.dict()
        )
