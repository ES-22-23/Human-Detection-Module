# @Author: Rafael Direito
# @Date:   2022-10-06 11:30:52 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-07 11:34:30


from human_detection import Human_Detection_Module
import os
import threading
from flask import Flask, jsonify, request

# AMQP Variables
RABBIT_MQ_URL = os.environ["RABBIT_HOST"]+ ":" +str(os.environ["RABBIT_PORT"])
RABBIT_MQ_USERNAME = os.environ["RABBIT_USER"]
RABBIT_MQ_PASSWORD = os.environ["RABBIT_PASSWORD"]
RABBIT_MQ_EXCHANGE_NAME = os.environ["RABBIT_HD_EXCHANGE_NAME"]
RABBIT_MQ_QUEUE_NAME = os.environ["RABBIT_HD_QUEUE"]

# OUTPUT
OUTPUT_DIR = "intruders"

FLASK_PORT = os.environ["FLASK_PORT"]

# creating a Flask app
app = Flask(__name__)

@app.route('/health', methods = ['GET'])
def home():
    if(request.method == 'GET'):
  
        return jsonify({'isHealthy': True, "additionalProperties": []})


threading.Thread(target=lambda: app.run(debug = False, port=FLASK_PORT)).start()

human_detection_worker = Human_Detection_Module(OUTPUT_DIR)

human_detection_worker.start_processing(
    broker_url=RABBIT_MQ_URL,
    broker_username=RABBIT_MQ_USERNAME,
    broker_password=RABBIT_MQ_PASSWORD,
    exchange_name=RABBIT_MQ_EXCHANGE_NAME,
    queue_name=RABBIT_MQ_QUEUE_NAME
    )
