import asyncio
import aio_pika
from app.core.config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS,
    CANDIDATE_EXCHANGE_NAME
)

class RabbitMQProducer:
    def __init__(self):
        self.connection_string = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        print("Connecting to RabbitMQ as a producer...")
        try:
            self.connection = await aio_pika.connect_robust(self.connection_string)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                CANDIDATE_EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
            )
            print("Successfully connected to RabbitMQ.")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")

    async def publish_message(self, routing_key: str, message_body: bytes):
        if not self.exchange:
            print("Cannot publish: not connected to RabbitMQ.")
            return

        message = aio_pika.Message(
            body=message_body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message, routing_key=routing_key)
        print(f"Published message with routing key '{routing_key}'")

    async def close(self):
        if self.connection:
            await self.connection.close()
        print("RabbitMQ producer connection closed.")

publisher = RabbitMQProducer()