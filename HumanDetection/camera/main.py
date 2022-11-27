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
CAMERA_ID = int(os.environ["CAM_ID"])
NUM_FRAMES_PER_SECOND_TO_PROCESS = 2

# AMQP Variables
RABBIT_MQ_URL = os.environ["RABBIT_HOST"]+ ":" +str(os.environ["RABBIT_PORT"])
RABBIT_MQ_USERNAME = os.environ["RABBIT_USER"]
RABBIT_MQ_PASSWORD = os.environ["RABBIT_PASSWORD"]
RABBIT_MQ_CAM_EXCHANGE_NAME = os.environ["RABBIT_CAM_EXCHANGE"]
RABBIT_MQ_HD_QUEUE_NAME = os.environ["RABBIT_HD_QUEUE"]
RABBIT_MQ_HD_EXCHANGE_NAME = os.environ["RABBIT_HD_EXCHANGE_NAME"]

IMAPI_URL = os.environ["IMAPI_HOST"] + ":8083"
SMAPI_URL = os.environ["SMAPI_HOST"] + ":8082" 

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


threading.Thread(target=lambda: app.run(debug = False, port=FLASK_PORT)).start()

camera = Camera(
    camera_id=CAMERA_ID,
    frames_per_second_to_process=NUM_FRAMES_PER_SECOND_TO_PROCESS,
    imapi_url= IMAPI_URL,
    smapi_url= SMAPI_URL,
    keycloak_url= KEYCLOAK_URL,
    client_id = KEYCLOAK_SMAPI_CLIENT_ID,
    username = KEYCLOAK_USERNAME,
    password = KEYCLOAK_PASSWORD,
    client_secret = KEYCLOAK_SMAPI_CLIENT_SECRET
    )

camera.attach_to_message_broker(
    broker_url=RABBIT_MQ_URL,
    broker_username=RABBIT_MQ_USERNAME,
    broker_password=RABBIT_MQ_PASSWORD,
    exchange_name=RABBIT_MQ_HD_EXCHANGE_NAME,
    queue_name=RABBIT_MQ_HD_QUEUE_NAME,
    )

async def mainLoop():
    send_video = asyncio.create_task(camera.consumer(exchange_name=RABBIT_MQ_CAM_EXCHANGE_NAME))

    await camera.transmit_video("samples/people-detection.mp4")

# loop = asyncio.get_event_loop()
# loop.run_until_complete(loopFogo())

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
    

