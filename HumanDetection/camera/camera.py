# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:23 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 12:02:59

import time
import cv2
import imutils
import kombu
import datetime
import json 
import requests
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import asyncio
#import socket

class Camera:

    kombu_connection = None
    kombu_exchange = None
    kombu_channel = None
    kombu_producer = None
    kombu_queue = None

    def __init__(self, frames_per_second_to_process,imapi_url,smapi_url, keycloak_url, client_id, username, password, client_secret, service_registry_url):
        self.frames_per_second_to_process = frames_per_second_to_process
        self.imapi_url = imapi_url
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
        #self.transmit_video_bool = False

        print("before getting token")
        token_response = requests.post(self.keycloak_url, data=self.smapi_data)
        token_response = token_response.json()
        print(token_response)
        self.access_token = "Bearer " + str(token_response["access_token"])
        print("before getting pub ip")
        public_ip = requests.get('https://v4.ident.me/').content.decode('utf8')
        print(public_ip)
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
        url =service_registry_url+ "/registry/register"
        print(url)
        #self.camera_id = requests.post(url, json=data, headers={"Authorization" : "Bearer "+str(self.access_token)}).json()["serviceUniqueId"]
        self.camera_id = "111cc11-165a-445a-b062-9b7a16195dd6"
        print(self.camera_id)
        #print(self.camera_id.text)


    # def disc_message(self, disc_url, ):
    #     response = requests.get(disc_url,self.property).json()
    #     self.camera_id = ...

    def attach_to_message_broker(self, broker_url, broker_username,
                                 broker_password, exchange_name, queue_name):
        # Create Connection String
        connection_string = f"amqps://{broker_username}:{broker_password}" \
            f"@{broker_url}/"

        print(connection_string)
        # Kombu Connection
        self.kombu_connection = kombu.Connection(connection_string, ssl=True)
        self.kombu_channel = self.kombu_connection.channel()

        # Kombu Exchange
        self.kombu_exchange = kombu.Exchange(
            name=exchange_name,
            type="direct",
            delivery_mode=1
        )

        # Kombu Producer
        self.kombu_producer = kombu.Producer(
            exchange=self.kombu_exchange,
            channel=self.kombu_channel
        )

        # Kombu Queue
        self.kombu_queue = kombu.Queue(
            name=queue_name,
            exchange=self.kombu_exchange
        )
        self.kombu_queue.maybe_bind(self.kombu_connection)
        self.kombu_queue.declare()


    def get_property_id(self):
        while self.propertyId == None:
            print("getting property id")
            self.propertyId=10
            # smapi_response = requests.get(self.smapi_url + "/cameras/" + str(self.camera_id), headers={"Authorization" : str(self.access_token)})
            # if (smapi_response.status_code == 200):
            #     smapi_response = smapi_response.json()
            #     self.propertyId = smapi_response["property"] #tenho que ver o que devolve
            #     print(self.propertyId)
            # else:
            #     print("Request Error. HTTP Error code: " + str(smapi_response.status_code))
            #     time.sleep(10)


    async def transmit_video(self, video_path):
        video = cv2.VideoCapture(video_path)

        # Check if the video exists
        check, frame = video.read()
        if not check:
            print("Video Not Found. Please Enter a Valid Path (Full path of " +
                  "Video Should be Provided).")
            return

        # Compute the frame step
        video_fps = video.get(cv2.CAP_PROP_FPS)
        frame_step = video_fps/self.frames_per_second_to_process
        print('Detecting people...')
        time_now = datetime.datetime.now()

        counter = 1
        frame_count = 0
        frame_id = 0
        while video.isOpened():

            # check is True if reading was successful
            check, frame = video.read()

            if check:
                if frame_count % frame_step == 0:

                    # Resize frame
                    frame = imutils.resize(
                        frame,
                        width=min(800, frame.shape[1])
                    )

                    # Encode to JPEG
                    result, imgencode = cv2.imencode(
                        '.jpg',
                        frame,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                    )

                    frame_seconds = frame_count/video_fps
                    time_now += datetime.timedelta(seconds=frame_seconds)

                    # send a message
                    self.kombu_producer.publish(
                        body=imgencode.tobytes(),
                        content_type='image/jpeg',
                        content_encoding='binary',
                        headers={
                            "source": f"camera_{self.camera_id}",
                            "timestamp": str(time_now),
                            "frame_count": frame_count,
                            "frame_id": frame_id
                        }
                    )
                    print(f"[Camera {self.camera_id}] Sent a frame to " +
                          "the human-detection module " +
                          f"(frame_number={frame_count}, " +
                          f"frame_timestamp={time_now})")

                    frame_id += 1
                    #key = cv2.waitKey(1)
                    #if key == ord('q'):
                    #    break
                    if counter % 100 == 0:
                        print("before sleep")
                        await asyncio.sleep(0)
                    counter += 1
            else:
                break
            
            frame_count += 1
            #await asyncio.sleep(0)
        #self.transmit_video_bool=True
        print("transmit_video_end")
        await asyncio.sleep(0) 


    def process_message(self, body, message):
        print("The following message has been received: %s" % body)
        #print(type(body))
        dict = json.loads(str(body))

        if dict["cameraId"] == self.camera_id and self.propertyId != None:
            print("getting property id")
            splitTimestamp = dict["timestamp"].split(" ")[-1].split(".")[0].split(":")
            timestamp = int(splitTimestamp[1])%10*60+int(splitTimestamp[-1])
            startTime= timestamp-180 
            endTime= timestamp+179 
            if startTime < 0:
                startTime= abs(startTime)
                endTime+= startTime*2 -1
            elif endTime >  590:
                startTime= endTime-590
                endTime= startTime+359
            ffmpeg_extract_subclip("samples/people-detection.mp4", startTime, endTime, targetname="temp.mp4")
            files = {'document': open("temp.mp4", 'rb')} # , 'name': "cam"+str(self.camera_id)+"Video"+dict["timestamp"]
            params = { 'name': "propId"+str(self.propertyId)+"cam"+str(self.camera_id)+"Video"+dict["timestamp"]}
            #userpass = b64encode(b"<username>:<password>").decode("ascii")
            # Check if the video exists
            #headers = {'Content-type':'multipart/form-data; boundary=562436211435313341'}#, 'Authorization': 'Basic ' + userpass}
            url = self.imapi_url+"/videoClips"
            print(url)
            #print(files["document"].peek())
            try:
                #response = requests.post(url, files=files, params=params, headers={"Authorization" : str(self.access_token)})
                print("no sending video")
                #print(response.text)
                #print("Request status: %s" % response.status_code)
            finally:
                os.remove("temp.mp4")
                print("Removing temp.mp4")

        print("end")
        message.ack()

    async def consumer(self,  exchange_name):


        # Kombu Exchange
        self.kombu_imapi_exchange = kombu.Exchange(
            name=exchange_name,
            type="direct",
            delivery_mode=1
        )

        # Kombu Queue
        self.kombu_imapi_queue = kombu.Queue(
            name="cam"+str(self.camera_id),
            exchange=self.kombu_imapi_exchange,
            routing_key="cam"
        )


        # Create the consumer
        with kombu.Consumer(self.kombu_connection, queues=self.kombu_imapi_queue, callbacks=[self.process_message],accept=["text/plain"]):

            while True:
                print("consuming...")
                #self.consumer.consume()
                try:
                    self.kombu_connection.drain_events(timeout=1)

                except TimeoutError:
                    print("No message received")
                finally:
                    await asyncio.sleep(0)





