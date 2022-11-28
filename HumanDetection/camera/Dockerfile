#Deriving the latest base image
FROM python:latest


# ARGS


ARG FLASK_PORT
ENV FLASK_PORT=1234

#Env variables
ENV RABBIT_HOST="b-0124c7d5-e02a-4de6-ba98-0043ea0219be.mq.eu-west-2.amazonaws.com"
ENV RABBIT_PORT=5671
ENV RABBIT_USER="admin"
ENV RABBIT_PASSWORD="EHgxSz7J7noeH2"
ENV RABBIT_CAM_EXCHANGE="get_video_clips"


ENV RABBIT_HD_QUEUE="human-detection-queue"
ENV RABBIT_HD_EXCHANGE_NAME="human-detection-exchange"


ENV IMAPI_HOST=scss.hgsoft.me
ENV SMAPI_HOST=scss.hgsoft.me
ENV SERVICE_REGISTRY_HOST=scss.hgsoft.me

ENV KEYCLOAK_URL=https://auth.hgsoft.me/realms/keycloak-react-auth/protocol/openid-connect/token

ENV KEYCLOAK_SMAPI_CLIENT_ID=sites-management-API
ENV KEYCLOAK_USERNAME="camera_user"
ENV KEYCLOAK_PASSWORD="camera_user"
ENV KEYCLOAK_SMAPI_CLIENT_SECRET=TiRdFEZFBNfJ92tq7iaHlP2u0y5dQ5le


# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /

#to COPY the remote file at working directory in container
COPY main.py ./
COPY requirements.txt requirements.txt



RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt


# Now the structure looks like this '/usr/app/src/test.py'

COPY . .
#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "./main.py"]