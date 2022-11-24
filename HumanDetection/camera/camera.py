# @Author: Rafael Direito
# @Date:   2022-10-06 10:54:23 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 12:02:59

import cv2
import imutils
import kombu
import datetime
import json 
import requests
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import asyncio


class Camera:

    kombu_connection = None
    kombu_exchange = None
    kombu_channel = None
    kombu_producer = None
    kombu_queue = None

    def __init__(self, frames_per_second_to_process,imapi_url,smapi_url, keycloak_url, client_id, username, password, client_secret, camera_id=-1):
        self.camera_id = camera_id
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

    def disc_message(self, disc_url, ):
        response = requests.get(disc_url,self.property).json()
        self.camera_id = ...

    def attach_to_message_broker(self, broker_url, broker_username,
                                 broker_password, exchange_name, queue_name):
        # Create Connection String
        connection_string = f"amqp://{broker_username}:{broker_password}" \
            f"@{broker_url}/"

        # Kombu Connection
        self.kombu_connection = kombu.Connection(connection_string)
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


    def process_message(self, body, message):
        print("The following message has been received: %s" % body)
        #print(type(body))
        dict = json.loads(str(body))
        if dict["cameraId"]==self.camera_id:
            if self.propertyId == None:
                token_response = requests.post(self.keycloak_url, data=self.smapi_data)
                token_response = token_response.json()
                access_token = "Bearer " + str(token_response["access_token"])
                smapi_response = requests.get("http://" + self.smapi_url + "/cameras/" + str(self.camera_id), headers={"Authorization" : str(access_token)})
                smapi_response = smapi_response.json()
                self.propertyId = smapi_response["property"] #tenho que ver o que devolve
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
            url = "http://"+self.imapi_url+"/videoClips"
            print(url)
            print(files["document"].peek())
            try:
                response = requests.post(url, files=files, params=params)
                #print(response.text)
                print("Request status: %s" % response.status_code)
            finally:
                os.remove("temp.mp4")
                print("Removing temp.mp4")

        print("end")

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
                    # print(f"[Camera {self.camera_id}] Sent a frame to " +
                    #       "the human-detection module " +
                    #       f"(frame_number={frame_count}, " +
                    #       f"frame_timestamp={time_now})")

                    frame_id += 1
                    #key = cv2.waitKey(1)
                    #if key == ord('q'):
                    #    break
            else:
                break

            frame_count += 1
            await asyncio.sleep(0)

    async def consumer(self,  queue_name):
        # connection_string = f"amqp://{broker_username}:{broker_password}" \
        # f"@{broker_url}/"

        # # Kombu Connection
        # self.kombu_connection = kombu.Connection(connection_string)
        # self.kombu_channel = self.kombu_connection.channel()

        # conn= self.kombu_connection.clone()
        # Kombu Exchange
        # self.kombu_imapi_exchange = kombu.Exchange(
        #     name=exchange_name,
        #     type="direct",
        #     delivery_mode=1
        # )
        # Kombu Queue
        self.kombu_imapi_queue = kombu.Queue(
            name=queue_name,
            #exchange=self.kombu_exchange
        )
        self.kombu_queue.maybe_bind(self.kombu_connection)
        self.kombu_queue.declare()

        # Create the consumer
        self.consumer=kombu.Consumer(self.kombu_connection, queues=self.kombu_imapi_queue, callbacks=[self.process_message],accept=["text/plain"])

        while True:
            self.consumer.consume()
            #self.kombu_connection.drain_events()
            await asyncio.sleep(0)





