# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:18 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 11:19:15
import os
from Alarm import Alarm
import sys

# ALARM VARIABLES
ALARM_ID = int(sys.argv[1])
NUM_FRAMES_PER_SECOND_TO_PROCESS = 2

# AMQP Variables
RABBIT_MQ_URL = os.environ["RABBIT_HOST"]+ ":" +str(os.environ["RABBIT_PORT"])
RABBIT_MQ_USERNAME = os.environ["RABBIT_USER"]
RABBIT_MQ_PASSWORD = os.environ["RABBIT_PASSWORD"]
RABBIT_MQ_IMAPI_QUEUE_NAME = os.environ["RABBIT_IMAPI_QUEUE"]
RABBIT_MQ_IMAPI_EXCHANGE_NAME = os.environ["RABBIT_PASSWORD"]

IMAPI_URL = os.environ["RABBIT_HOST"] + ":8083" 

# RABBIT_MQ_URL = "localhost:5672"
# RABBIT_MQ_USERNAME = "myuser"
# RABBIT_MQ_PASSWORD = "mypassword"
# RABBIT_MQ_EXCHANGE_NAME = "human-detection-exchange"
# RABBIT_MQ_HD_QUEUE_NAME = "human-detection-queue"





alarm = Alarm(
    alarm_id=ALARM_ID,
    frames_per_second_to_process=NUM_FRAMES_PER_SECOND_TO_PROCESS,
    imapi_url= IMAPI_URL,
    property="DETI"
    )


print("End of video transmission")

alarm.consumer(
    #exchange_name=RABBIT_MQ_IMAPI_EXCHANGE_NAME,
    queue_name=RABBIT_MQ_IMAPI_QUEUE_NAME,
    broker_url=RABBIT_MQ_URL,
    broker_username=RABBIT_MQ_USERNAME,
    broker_password=RABBIT_MQ_PASSWORD,
)


