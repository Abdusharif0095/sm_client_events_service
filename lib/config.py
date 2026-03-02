import os
from dotenv import load_dotenv
from configparser import ConfigParser


load_dotenv('lib/configs.env')


class Settings:
    PROJECT_NAME: str = "SM Client Event Service"
    PROJECT_VERSION: str = "2.0.2"

    KAFKA_BROKER: str = os.getenv("KAFKA_BROKER")
    ALERTS_TOPIC: str = os.getenv("ALERTS_TOPIC")
    CLIENT_EVENTS_TOPIC: str = os.getenv("CLIENT_EVENTS_TOPIC")
    PING_RESPONSES_TOPIC: str = os.getenv("PING_RESPONSES_TOPIC")

    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: str = os.getenv("REDIS_PORT")


settings = Settings()


class Keys:
    def __init__(self):
        with open('lib/private.pem', 'rb') as f:
            self.privatekey = f.read()
        with open("lib/public.pem","rb") as f:
            self.publickey=f.read()
        
def configdb(filename='lib/configs.env', section='postgresql'):
    return get_section(section, filename)

def get_section(section, filename='lib/configs.env'):
    parser = ConfigParser()
    parser.read(filename, encoding='UTF-8')
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db