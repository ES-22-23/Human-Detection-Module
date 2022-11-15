# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:23 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 12:02:59

import cv2
import imutils
import kombu
import datetime
import json 
import requests

import asyncio

class Alarm:

    kombu_connection = None
    kombu_exchange = None
    kombu_channel = None
    kombu_producer = None
    kombu_queue = None

    def __init__(self, imapi_url,property, alarm_id=-1, state=False):
        self.alarm_id = alarm_id
        self.imapi_url = imapi_url
        self.property = property
        self.state = state

    def disc_message(self, disc_url, ):
        response = requests.get(disc_url,self.property).json()
        self.alarm_id = ...



    def attach_to_message_broker(self, broker_url, broker_username,
                                 broker_password, exchange_name, queue_name):
        # Create Connection String
        connection_string = f"amqp://{broker_username}:{broker_password}" \
            f"@{broker_url}/"

        # Kombu Connection
        self.kombu_connection = kombu.Connection(connection_string)
        self.kombu_channel = self.kombu_connection.channel()

        # Kombu Exchange
        self.kombu_exchange = kombu.Exchange(
            name=exchange_name,
            type="direct",
            delivery_mode=1
        )

        # Kombu Producer
        self.kombu_producer = kombu.Producer(
            exchange=self.kombu_exchange,
            channel=self.kombu_channel
        )

        # Kombu Queue
        self.kombu_queue = kombu.Queue(
            name=queue_name,
            exchange=self.kombu_exchange
        )
        self.kombu_queue.maybe_bind(self.kombu_connection)
        self.kombu_queue.declare()


    def process_message(self, body, message):
        print("The following message has been received: %s" % body)

        dict = json.loads(str(body))
        if dict["alarmId"]==self.alarm_id:
            self.state = dict["state"]
        print("end")

    def consumer(self, broker_url, broker_username,
                                 broker_password, exchange_name, queue_name):
        connection_string = f"amqp://{broker_username}:{broker_password}" \
        f"@{broker_url}/"

        # Kombu Connection
        self.kombu_connection = kombu.Connection(connection_string)
        self.kombu_channel = self.kombu_connection.channel()

        # Kombu Queue
        self.kombu_imapi_queue = kombu.Queue(
            name=queue_name,
            #exchange=self.kombu_exchange
        )
        self.kombu_queue.maybe_bind(self.kombu_connection)
        self.kombu_queue.declare()

        # Create the consumer
        self.consumer=kombu.Consumer(self.kombu_connection, queues=self.kombu_imapi_queue, callbacks=[self.process_message],accept=["text/plain"])

        self.consumer.consume()
        self.kombu_connection.drain_events()





