from contextlib import contextmanager
from typing import Union

import pika
from pika.adapters.blocking_connection import BlockingChannel

connection = None
channel: Union[BlockingChannel, None] = None

@contextmanager
def get_pika():
    global connection
    global channel
    try:
        if channel and channel.is_open:
            yield channel
        conn_params = pika.ConnectionParameters(host='localhost', port=5672, credentials=pika.PlainCredentials(username="gamenode", password="gamenode"))
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
