import json
from connections.connection import connection


async def get_user_device_data(user_uuid: str):
    result = None
    with connection('sm_identities') as cur:
        cur.execute('select auth.get_user_device_data(%s)', (user_uuid,))
        result = cur.fetchone()[0]
    return result


async def add_push_notification(user_uuid: str, device_uuid: str, device_token: str, title: str, body: str, notification_type: str, additional_data: dict):
    with connection('standart_moliya') as cur:
        cur.execute(
            'call push_notifications.add_push_notification_from_back_srv(%s, %s, %s, %s, %s, %s, %s)',
            [user_uuid, device_uuid, device_token, title, body, notification_type, json.dumps(additional_data)]
        )
    return
