# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:18 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 11:19:15
import os
from alarm import Alarm
import sys
import asyncio
import threading
from flask import Flask, jsonify, request

# creating a Flask app
app = Flask(__name__)


# AMQP Variables
RABBIT_MQ_URL = os.environ["RABBIT_HOST"]+ ":" +str(os.environ["RABBIT_PORT"])
RABBIT_MQ_USERNAME = os.environ["RABBIT_USER"]
RABBIT_MQ_PASSWORD = os.environ["RABBIT_PASSWORD"]
RABBIT_ALARM_EXCHANGE = os.environ["RABBIT_ALARM_EXCHANGE"]

SMAPI_URL =  os.environ["SMAPI_HOST"] 
SERVICE_REGISTRY_URL =  os.environ["SERVICE_REGISTRY_HOST"] 

KEYCLOAK_URL = os.environ["KEYCLOAK_URL"]
KEYCLOAK_SMAPI_CLIENT_ID = os.environ["KEYCLOAK_SMAPI_CLIENT_ID"]
KEYCLOAK_USERNAME = os.environ["KEYCLOAK_USERNAME"]
KEYCLOAK_PASSWORD = os.environ["KEYCLOAK_PASSWORD"]
KEYCLOAK_SMAPI_CLIENT_SECRET = os.environ["KEYCLOAK_SMAPI_CLIENT_SECRET"]


FLASK_PORT = os.environ["FLASK_PORT"]

@app.route('/health', methods = ['GET'])
def home():
    if(request.method == 'GET'):
  
        return jsonify({'isHealthy': True, "additionalProperties": []})


@app.route('/isringing', methods = ['GET'])
def ringing():
    if(request.method == 'GET'):
  
        return jsonify({'isringing': alarm.is_on})


threading.Thread(target=lambda: app.run(debug = False, port=FLASK_PORT)).start()

alarm = Alarm(
    smapi_url= SMAPI_URL,
    keycloak_url= KEYCLOAK_URL,
    client_id = KEYCLOAK_SMAPI_CLIENT_ID,
    username = KEYCLOAK_USERNAME,
    password = KEYCLOAK_PASSWORD,
    client_secret = KEYCLOAK_SMAPI_CLIENT_SECRET,
    service_registry_url=SERVICE_REGISTRY_URL
    )

async def loopFogo():
    asyncio.create_task(alarm.consumer(
        broker_url=RABBIT_MQ_URL,
        kombu_imapi_exchange=RABBIT_ALARM_EXCHANGE,
        broker_username=RABBIT_MQ_USERNAME,
        broker_password=RABBIT_MQ_PASSWORD,
        ))

alarm.get_property_id()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.create_task(loopFogo())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()
print("Final")

#asyncio.run(loopFogo())

# # driver function
# if __name__ == '__main__':
  
#     threading.Thread(target=lambda: app.run(debug = False, port=1234)).start()