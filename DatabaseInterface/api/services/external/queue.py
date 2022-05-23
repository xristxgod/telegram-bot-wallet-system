import json
from typing import Optional, Dict

import pika

from api.services.external.sender import Sender
from config import Config, logger

class Queue:
    """
    This class is used to send messages to RabbitMQ
    """
    RABBITMQ_URL = Config.RABBITMQ_URL

    @staticmethod
    def send_message(queue_name: str, message: Dict) -> bool:
        connection: Optional[pika.BlockingConnection] = None
        try:
            connection = pika.BlockingConnection(parameters=pika.URLParameters(Queue.RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            return True
        except Exception as error:
            logger.error(f"ERROR: {error}")
            Sender.send_message_to_checker(text=f"{error} | {message}")
            return False
        finally:
            if connection is not None:
                connection.close()