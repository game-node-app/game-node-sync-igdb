from config.rabbitmq import get_pika
import pika


def run():
    with get_pika() as pika:
        pika.confirm_delivery()
        pika.basic_publish(exchange="sync", routing_key="igdb-sync", body="Hello from IGDB!")


if __name__ == "__main__":
    run()
