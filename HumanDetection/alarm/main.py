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

# ALARM VARIABLES
ALARM_ID = int(os.environ["ALARM_ID"])

# AMQP Variables
RABBIT_MQ_URL = os.environ["RABBIT_HOST"]+ ":" +str(os.environ["RABBIT_PORT"])
RABBIT_MQ_USERNAME = os.environ["RABBIT_USER"]
RABBIT_MQ_PASSWORD = os.environ["RABBIT_PASSWORD"]
RABBIT_ALARM_QUEUE = os.environ["RABBIT_ALARM_QUEUE"]

IMAPI_URL = os.environ["RABBIT_HOST"] + ":8083" 

# RABBIT_MQ_URL = "localhost:5672"
# RABBIT_MQ_USERNAME = "myuser"
# RABBIT_MQ_PASSWORD = "mypassword"
# RABBIT_MQ_EXCHANGE_NAME = "human-detection-exchange"
# RABBIT_MQ_HD_QUEUE_NAME = "human-detection-queue"


@app.route('/health', methods = ['GET'])
def home():
    if(request.method == 'GET'):
  
        return jsonify({'isAvailable': True})


threading.Thread(target=lambda: app.run(debug = False, port=1235)).start()


alarm = Alarm(
    alarm_id=ALARM_ID,
    imapi_url= RABBIT_MQ_URL,
    )



async def loopFogo():
    asyncio.create_task(alarm.consumer(
        queue_name=RABBIT_ALARM_QUEUE,
        broker_username=RABBIT_MQ_USERNAME,
        broker_password=RABBIT_MQ_PASSWORD,
        ))



loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(loopFogo())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()
#asyncio.run(loopFogo())

# # driver function
# if __name__ == '__main__':
  
#     threading.Thread(target=lambda: app.run(debug = False, port=1234)).start()
    

