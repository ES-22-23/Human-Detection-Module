# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:23 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 12:02:59

import kombu
import datetime
import json 
import requests
import os
import asyncio
import time


class Alarm:

    kombu_connection = None
    kombu_exchange = None
    kombu_channel = None
    kombu_producer = None
    kombu_queue = None

    def __init__(self, imapi_url, alarm_id=-1):
        self.alarm_id = alarm_id
        self.imapi_url = imapi_url
        self.is_on = False




    def process_message(self, body, message):
        print("The following message has been received: %s" % body)
        #print(type(body))
        try:
            dict = json.loads(str(body))
            if dict["cameraId"]==self.alarm_id:
                self.is_on = True
                print("Alarm is on")
                #time.sleep(2.5)
                self.is_on = False
                print("Alarm is Off")
        finally:
            print("end")
            message.ack()

    

    async def consumer(self,  queue_name,broker_username,broker_password):
        connection_string = f"amqp://{broker_username}:{broker_password}" \
        f"@{self.imapi_url}/"


        print(connection_string)
        # Kombu Connection
        self.kombu_connection = kombu.Connection(connection_string)
        self.kombu_channel = self.kombu_connection.channel()


        # Kombu Queue
        self.kombu_imapi_queue = kombu.Queue(
            name=queue_name,
            #exchange=self.kombu_exchange
        )

        print(queue_name)
        # Create the consumer
        with kombu.Consumer(self.kombu_connection, queues=self.kombu_imapi_queue, callbacks=[self.process_message],accept=["text/plain"]):

            while True:
                print("consuming...")
                #self.consumer.consume()
                self.kombu_connection.drain_events()
                await asyncio.sleep(0)





