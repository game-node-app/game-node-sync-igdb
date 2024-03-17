from contextlib import contextmanager
from typing import Union
import os

import pika
from pika.adapters.blocking_connection import BlockingChannel

connection = None
channel: Union[BlockingChannel, None] = None

def _get_connection_parameters():
    host = os.environ.get("RABBITMQ_HOST")
    port = os.environ.get("RABBITMQ_PORT")
    username = os.environ.get("RABBITMQ_USERNAME")
    password = os.environ.get("RABBITMQ_PASSWORD")
    return pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(username=username, password=password))

@contextmanager
def get_pika():
    global connection
    global channel
    try:
        if channel is not None and channel.is_open:
            yield channel
        conn_params = _get_connection_parameters()
        connection = pika.BlockingConnection(conn_params)
        channel = connection.channel()
        yield channel
    except Exception as e:
        print(e)
        if channel.is_open:
            channel.close()
        if connection.is_open:
            connection.close()

    finally:
        if channel.is_open:
            channel.close()
        if connection.is_open:
            connection.close()
    pass
