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
#import socket

class Alarm:

    kombu_connection = None
    kombu_exchange = None
    kombu_channel = None
    kombu_producer = None
    kombu_queue = None

    def __init__(self,  smapi_url, keycloak_url, client_id, username, password, client_secret, service_registry_url):
        self.is_on = False
        self.smapi_url = smapi_url
        self.keycloak_url = keycloak_url
        self.propertyId = None

        #needed for keycloak
        self.client_id = client_id
        self.username = username
        self.password = password
        self.grant_type = "password"
        self.client_secret = client_secret
        self.smapi_data = {'client_id': self.client_id, 'username': self.username, 'password':self.password, 'grant_type': self.grant_type, 'client_secret': self.client_secret}

        token_response = requests.post(self.keycloak_url, data=self.smapi_data)
        token_response = token_response.json()
        #print(token_response)
        access_token = "Bearer " + str(token_response["access_token"])
        public_ip = requests.get('https://api.ipify.org').content.decode('utf8')
        private_ip = "10.0.10.2" #socket.gethostbyname(socket.gethostname())

        data = {
            "serviceName": "Camera",
            "serviceType": "CAMERA",
            "serviceHealthEndpoint": "/health",
            "serviceProtocol": "HTTP",
            "serviceAddress": {
                "public": public_ip,
                "private": private_ip
            }
        }
        url =service_registry_url+ "registry/register"
        self.alarm_id = requests.post(url, json=data, headers={"Authorization" : str(access_token)}).json()["serviceUniqueId"]
        print(self.alarm_id)


    def get_property_id(self):
        while self.propertyId == None:
            print("getting property id")
            token_response = requests.post(self.keycloak_url, data=self.smapi_data)
            token_response = token_response.json()
            access_token = "Bearer " + str(token_response["access_token"])
            print(access_token)
            smapi_response = requests.get(self.smapi_url + "/alarms/" + str(self.alarm_id), headers={"Authorization" : str(access_token)})
            if (smapi_response.status_code == 200):
                smapi_response = smapi_response.json()
                self.propertyId = smapi_response["property"] #tenho que ver o que devolve
                print(self.propertyId)
            else:
                print("Request Error. HTTP Error code: " + str(smapi_response.status_code))
                time.sleep(10)

    def process_message(self, body, message):
        print("The following message has been received: %s" % body)
        #print(type(body))
        try:
            dict = json.loads(str(body))
            if dict["propertyId"]==self.propertyId:
                self.is_on = True
                print("Alarm is on")
                #time.sleep(2.5)
                self.is_on = False
                print("Alarm is Off")
        finally:
            print("end")
            message.ack()

    async def consumer(self,  kombu_imapi_exchange,broker_username,broker_password, broker_url):
        connection_string = f"amqps://{broker_username}:{broker_password}" \
        f"@{broker_url}/"


        print(connection_string)
        # Kombu Connection
        self.kombu_connection = kombu.Connection(connection_string)
        self.kombu_channel = self.kombu_connection.channel()


        # Kombu Queue
        self.kombu_imapi_queue = kombu.Queue(
            name="alarm"+str(self.alarm_id),
            exchange=kombu_imapi_exchange,
            routing_key="alarm"
        )

        print(kombu_imapi_exchange)
        # Create the consumer
        with kombu.Consumer(self.kombu_connection, queues=self.kombu_imapi_queue, callbacks=[self.process_message],accept=["text/plain"]):

            while True:
                print("consuming...")
                #self.consumer.consume()
                self.kombu_connection.drain_events()
                await asyncio.sleep(0)