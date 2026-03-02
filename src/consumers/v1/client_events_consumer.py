import json
import asyncio
import traceback
from typing import Dict
from datetime import datetime

import connections.kafka_connection as kafka
from kafka import TopicPartition, OffsetAndMetadata


from src.modules.v1 import crud
from src.models.models import Alert
from src.models.models import EventModel
from src.endpoints.v1.main import manager
from src.producers.alert_producer import AlertProducer


async def run():
    consumer = kafka.get_consumer(
        topic='client_events_topic',
        group_id='client_events_senders',
        auto_offset_reset='earliest',
        enable_auto_commit=False,
    )

    try:
        while True:
            records = await asyncio.to_thread(consumer.poll, timeout_ms=1000)

            if not records:
                await asyncio.sleep(0.1)
                continue

            offsets: Dict[TopicPartition, OffsetAndMetadata] = {}

            for tp, messages in records.items():
                for msg in messages:
                    err, processed = await process_message(msg)
                    if not processed:
                        producer = AlertProducer()
                        await producer.start()
                        try:
                            alert = Alert(
                                layer="python",
                                service="Client event Service",
                                function="client_event_consumer.run",
                                error=err,
                                datetime=datetime.now().isoformat(),
                                comment=""
                            )

                            await producer.send_alert(alert)
                        finally:
                            await producer.stop()

                    offsets[tp] = OffsetAndMetadata(msg.offset + 1, None)

            if offsets:
                await asyncio.to_thread(consumer.commit, offsets=offsets)
    finally:
        consumer.close()


async def process_message(msg):
    try:
        print("Received message:", msg, flush=True)
        json_value = json.loads(msg.value)
        event_model = EventModel(**json_value)

        if event_model.event_type == 'chat_msg':
            await handle_chat_message(event_model)
        elif event_model.event_type == 'trn_msg':
            await handle_trn_message(event_model)
        elif event_model.event_type == 'notification':
            await handle_notification(event_model)
        elif event_model.event_type == 'ping':
            await handle_ping(event_model)
        else:
            print(f"Unsupported event type: {event_model.event_type}", flush=True)
        return "", True
    except KeyError as ke:
        print(f"KeyError in message processing: {ke}", flush=True)
        return f"KeyError in message processing: {ke}", False
    except ValueError as ve:
        print(f"ValueError in message processing: {ve}", flush=True)
        return f"ValueError in message processing: {ve}", False
    except Exception as ex:
        print(f"Client Events Consumer: Exception was caught: {ex}", flush=True)
        traceback.print_exc()
        return f"Client Events Consumer: Exception was caught: {ex}", False


async def handle_chat_message(event_model: EventModel):
    message = event_model.payload
    try:
        to_user_id = message.get('to_user_id')
        if to_user_id:
            del message["to_user_id"]
        data = await convert_data_format(message, event_model.event_type)
        print(f"Sending message to user {to_user_id}")
        send_res = await manager.send_message_async(to_user_id, data)
        if send_res == "user_not_connected":
            user_device_data = await crud.get_user_device_data(
                user_uuid=to_user_id
            )

            await crud.add_push_notification(
                user_uuid=to_user_id,
                device_uuid=user_device_data['device_uuid'],
                device_token=user_device_data['device_token'],
                title="Поддержка",
                body="Вам отправлено новое сообщение",
                notification_type="notification-chat",
                additional_data={"from": "client_event_service"}
            )
    except Exception as ws_error:
        print(f"Error sending message to WebSocket: {ws_error}", flush=True)
        raise


async def handle_trn_message(event_model: EventModel):
    message = event_model.payload
    try:
        to_user_id = message.get('user_uuid')
        if to_user_id:
            del message["user_uuid"]
        data = await convert_data_format(message, event_model.event_type)
        print(f"Sending message to user : {to_user_id}")
        await manager.send_message_async(to_user_id, data)
    except Exception as ws_error:
        print(f"Error sending message to WebSocket: {ws_error}", flush=True)
        raise


async def handle_notification(event_model: EventModel):
    message = event_model.payload
    try:
        to_user_id = message.get('user_uuid')
        if to_user_id:
            del message["user_uuid"]
        data = await convert_data_format(message, event_model.event_type)
        print(f"Sending message to user: {to_user_id}")
        await manager.send_message_async(to_user_id, data)
    except Exception as ws_error:
        print(f"Error sending message to WebSocket: {ws_error}", flush=True)
        raise


async def handle_ping(event_model: EventModel):
    message = event_model.payload
    try:
        to_user_uuid = message.get("user_uuid")
        if to_user_uuid:
            del message["user_uuid"]
        data = await convert_data_format(message, event_model.event_type)
        print(f"Sending message to user: {to_user_uuid}")
        await manager.send_message_async(to_user_uuid, data)
    except Exception as ws_error:
        print(f"Error sending message to WebSocket: {ws_error}", flush=True)


async def convert_data_format(data, event_type):
    return {"event_type": event_type, "data": data}
