from kafka import KafkaConsumer

def get_consumer(topic: str, group_id: str, auto_offset_reset: str, enable_auto_commit: bool):
    return KafkaConsumer(topic,
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset=auto_offset_reset,
                         enable_auto_commit=enable_auto_commit,
                         group_id=group_id,
                         value_deserializer=lambda x: x.decode('utf-8')
                        )