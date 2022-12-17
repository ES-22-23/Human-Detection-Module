# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:23 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 12:02:59

import kombu
#from datetime import datetime
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

    def __init__(self, smapi_url, keycloak_url, registry_client_id, username, password, registry_client_secret, service_registry_url):
        self.is_on = False
        self.smapi_url = smapi_url
        self.keycloak_url = keycloak_url
        self.propertyId = None

        #needed for keycloak
        self.registry_client_id = registry_client_id
        self.username = username
        self.password = password
        self.grant_type = "password"
        self.registry_client_secret = registry_client_secret
        self.keycloack_json = {'client_id': self.registry_client_id, 'username': self.username, 'password':self.password, 'grant_type': self.grant_type, 'client_secret': self.registry_client_secret}
        self.last_ring = None

        token_response = requests.post(self.keycloak_url, data=self.keycloack_json)
        token_response = token_response.json()
        #print(token_response)
        access_token =  str(token_response["access_token"])
        public_ip = requests.get('https://v4.ident.me/').content.decode('utf8')
        private_ip = "10.0.10.2" #socket.gethostbyname(socket.gethostname())

        data = {
            "serviceName": "Alarm",
            "serviceType": "ALARM",
            "serviceHealthEndpoint": "/health",
            "serviceProtocol": "HTTP",
            "serviceAddress": {
                "public": public_ip,
                "private": private_ip
            }
        }
        url =service_registry_url+ "/registry/register"
        print(url)
        self.alarm_id = requests.post(url, json=data, headers={"Authorization" : str(access_token)}).json()["serviceUniqueId"]
        print(self.alarm_id)
        #self.alarm_id = "e988df0c-6a23-49e5-a6a2-9b714fbaf4da"
        #print(self.alarm_id)


    def get_property_id(self,smapi_client_id, smapi_client_secret):
        while self.propertyId == None:
            print("getting property id")
            smapi_data = {'client_id': smapi_client_id, 'username': self.username, 'password':self.password, 'grant_type': self.grant_type, 'client_secret': smapi_client_secret}
            print(smapi_data)
            token_response = requests.post(self.keycloak_url, data=smapi_data)
            token_response = token_response.json()
            access_token= "Bearer " + str(token_response["access_token"])
            smapi_response = requests.get(self.smapi_url + "/alarms/" + str(self.alarm_id), headers={"Authorization" : str(access_token)})
            print(smapi_response)
            #self.propertyId = 10
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
                #msg_time = datetime.strptime(dict["timestamp"].split(".")[0], '%Y-%m-%d %H:%M:%S')
                #if self.last_ring == None or (msg_time-self.last_ring).total_seconds()>30:
                self.is_on = True
                print("Alarm is on")
                time.sleep(30)
                self.is_on = False
                print("Alarm is Off")
                #self.last_ring = msg_time
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
                #try:
                self.kombu_connection.drain_events()

                #except TimeoutError:
                #    print("No message received")
                #finally:
                #    await asyncio.sleep(0)
