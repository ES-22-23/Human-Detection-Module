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

from flask import Flask, jsonify, request
  
# creating a Flask app
app = Flask(__name__)

# CAMERA VARIABLES
CAMERA_ID = int(sys.argv[1])
NUM_FRAMES_PER_SECOND_TO_PROCESS = 2

# AMQP Variables
RABBIT_MQ_URL = os.environ["RABBIT_HOST"]+ ":" +str(os.environ["RABBIT_PORT"])
RABBIT_MQ_USERNAME = os.environ["RABBIT_USER"]
RABBIT_MQ_PASSWORD = os.environ["RABBIT_PASSWORD"]
RABBIT_MQ_IMAPI_QUEUE_NAME = os.environ["RABBIT_IMAPI_QUEUE"]
RABBIT_MQ_IMAPI_EXCHANGE_NAME = os.environ["RABBIT_PASSWORD"]
RABBIT_MQ_HD_QUEUE_NAME = os.environ["RABBIT_HD_QUEUE"]
RABBIT_MQ_HD_EXCHANGE_NAME = os.environ["RABBIT_HD_EXCHANGE_NAME"]

IMAPI_URL = os.environ["RABBIT_HOST"] + ":8083" 

# RABBIT_MQ_URL = "localhost:5672"
# RABBIT_MQ_USERNAME = "myuser"
# RABBIT_MQ_PASSWORD = "mypassword"
# RABBIT_MQ_EXCHANGE_NAME = "human-detection-exchange"
# RABBIT_MQ_HD_QUEUE_NAME = "human-detection-queue"


# @app.route('/', methods = ['GET', 'POST'])
# def home():
#     if(request.method == 'GET'):
  
#         data = "hello world"
#         return jsonify({'data': data})


camera = Camera(
    camera_id=CAMERA_ID,
    frames_per_second_to_process=NUM_FRAMES_PER_SECOND_TO_PROCESS,
    imapi_url= IMAPI_URL,
    property="DETI"
    )

camera.attach_to_message_broker(
    broker_url=RABBIT_MQ_URL,
    broker_username=RABBIT_MQ_USERNAME,
    broker_password=RABBIT_MQ_PASSWORD,
    exchange_name=RABBIT_MQ_HD_EXCHANGE_NAME,
    queue_name=RABBIT_MQ_HD_QUEUE_NAME,
    )

async def loopFogo():
    print("teste1")    
    transmit_video = asyncio.create_task(camera.consumer(queue_name=RABBIT_MQ_IMAPI_QUEUE_NAME))

    print("teste2")
    await camera.transmit_video("samples/people-detection.mp4")

loop = asyncio.get_event_loop()
loop.run_until_complete(loopFogo())

# driver function
# if __name__ == '__main__':
  
#     app.run(debug = True)
    

