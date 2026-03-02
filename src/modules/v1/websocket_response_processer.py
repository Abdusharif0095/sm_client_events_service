import json
import traceback
from datetime import datetime

from src.models import models
from connections import (
    redis_connection as redis,
    kafka_connection as kafka    
)
from src.modules.v1 import crud


def get_time_diff_on_milliseconds(start: str, end: str):
    tm1 = datetime.strptime(start, "%Y-%m-%d %H:%M:%S.%f")
    tm2 = datetime.strptime(end, "%Y-%m-%d %H:%M:%S.%f")
    time_diff = tm2 - tm1
    milliseconds = time_diff.total_seconds() * 1000
    return milliseconds


async def process_received_text(message: str, headers: dict):
    try:
        message_json = json.loads(message)
        response = models.ResponseModel(**message_json)
        
        if response.event_type == "pong":
            print(f"get pong event_type text: {message}, headers: {headers} status: processed", flush=True)
            await pong_handler(response, headers)
        else:
            print(f"get unregognized event_type text: {message}, status: not_processed", flush=True)
    except Exception as e:
        traceback.print_exc()
        print(f"get text: {message}, status: not_processed, error: {e}")
        raise

async def pong_handler(response: models.ResponseModel, headers: dict):
    message = response.payload
    try:
        ping_uuid = message["ping_uuid"]
        ping_data = await redis.get_ping_data_from_redis(ping_uuid)

        if not ping_data:
            pong_time = str(datetime.now())

            ping_response = models.PingResponse(
                ping_uuid=ping_uuid,
                pong_time=pong_time,
                pong_ip_address=headers.get("x-real-ip", None),
                ttl=0,
                comment="ping data not found"
            )

            print(f"Sending pong event to kafka: {ping_response}", flush=True)

            kafka.send_ping_response(message["ping_uuid"], ping_response)
        else:
            pong_device_data = await crud.get_user_device_data(ping_data.user_uuid)
            pong_device_uuid = pong_device_data.get("device_uuid", None)
            pong_time = str(datetime.now())

            ping_response = models.PingResponse(
                ping_uuid=ping_uuid,
                user_uuid=ping_data.user_uuid,
                ping_device_uuid=ping_data.ping_device_uuid,
                ping_time=ping_data.ping_time,
                pong_device_uuid=pong_device_uuid,
                pong_time=pong_time,
                pong_ip_address=headers.get("x-real-ip", None),
                ttl=get_time_diff_on_milliseconds(ping_data.ping_time, pong_time),
                comment=""
            )

            print(f"Sending pong event to kafka: {ping_response}", flush=True)

            kafka.send_ping_response(message["ping_uuid"], ping_response)
    except Exception as kafka_error:
        traceback.print_exc()
        print(f"Error sending pong event to Kafka: {kafka_error}", flush=True)
        raise
