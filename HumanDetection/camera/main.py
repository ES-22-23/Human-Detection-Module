# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:18 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 11:19:15
import os
from camera import Camera
import sys
import asyncio
import threading
from flask import Flask, jsonify, request

# creating a Flask app
app = Flask(__name__)

# CAMERA VARIABLES
NUM_FRAMES_PER_SECOND_TO_PROCESS = 2

# AMQP Variables

RABBIT_MQ_URL = os.environ["RABBIT_HOST"]+ ":" +str(os.environ["RABBIT_PORT"])
RABBIT_MQ_USERNAME = os.environ["RABBIT_USER"]
RABBIT_MQ_PASSWORD = os.environ["RABBIT_PASSWORD"]
RABBIT_MQ_CAM_EXCHANGE_NAME = os.environ["RABBIT_CAM_EXCHANGE"]
RABBIT_MQ_HD_QUEUE_NAME = os.environ["RABBIT_HD_QUEUE"]
RABBIT_MQ_HD_EXCHANGE_NAME = os.environ["RABBIT_HD_EXCHANGE_NAME"]

IMAPI_URL =  os.environ["IMAPI_HOST"] 
SMAPI_URL =  os.environ["SMAPI_HOST"] 
SERVICE_REGISTRY_URL =  os.environ["SERVICE_REGISTRY_HOST"] 

KEYCLOAK_URL = os.environ["KEYCLOAK_URL"]
KEYCLOAK_USERNAME = os.environ["KEYCLOAK_USERNAME"]
KEYCLOAK_PASSWORD = os.environ["KEYCLOAK_PASSWORD"]
KEYCLOAK_SMAPI_CLIENT_ID = os.environ["KEYCLOAK_SMAPI_CLIENT_ID"]
KEYCLOAK_SMAPI_CLIENT_SECRET = os.environ["KEYCLOAK_SMAPI_CLIENT_SECRET"]

KEYCLOAK_REGISTRY_CLIENT_ID = os.environ["KEYCLOAK_REGISTRY_CLIENT_ID"]
KEYCLOAK_REGISTRY_CLIENT_SECRET = os.environ["KEYCLOAK_REGISTRY_CLIENT_SECRET"]
N_CONSECUTIVE_MSG =os.environ["N_CONSECUTIVE_MSG"]


FLASK_PORT = os.environ["FLASK_PORT"]

@app.route('/health', methods = ['GET'])
def home():
    if(request.method == 'GET'):
  
        return jsonify({'isHealthy': True, "additionalProperties": []})


print("initialize camera")
camera = Camera(
    frames_per_second_to_process=NUM_FRAMES_PER_SECOND_TO_PROCESS,
    imapi_url= IMAPI_URL,
    smapi_url= SMAPI_URL,
    keycloak_url= KEYCLOAK_URL,
    registry_client_id = KEYCLOAK_REGISTRY_CLIENT_ID,
    username = KEYCLOAK_USERNAME,
    password = KEYCLOAK_PASSWORD,
    registry_client_secret = KEYCLOAK_REGISTRY_CLIENT_SECRET,
    service_registry_url=SERVICE_REGISTRY_URL,
    n_consecutive_msg=N_CONSECUTIVE_MSG,
    )

print("attach_to_message_broker")

camera.attach_to_message_broker(
    broker_url=RABBIT_MQ_URL,
    broker_username=RABBIT_MQ_USERNAME,
    broker_password=RABBIT_MQ_PASSWORD,
    exchange_name=RABBIT_MQ_HD_EXCHANGE_NAME,
    queue_name=RABBIT_MQ_HD_QUEUE_NAME,
    )

threading.Thread(target=lambda: app.run(debug = False, port=FLASK_PORT, host="0.0.0.0",threaded=True)).start()
async def mainLoop():
    asyncio.create_task(camera.consumer(exchange_name=RABBIT_MQ_CAM_EXCHANGE_NAME))
    await camera.transmit_video("samples/people-detection.mp4")


# loop = asyncio.get_event_loop()
# loop.run_until_complete(loopFogo())
print("get property id")

camera.get_property_id(KEYCLOAK_SMAPI_CLIENT_ID,KEYCLOAK_SMAPI_CLIENT_SECRET)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.create_task(mainLoop())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()
print("Final")

# # driver function
# if __name__ == '__main__':
  
#     threading.Thread(target=lambda: app.run(debug = False, port=1234)).start()
    

