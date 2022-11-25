#Deriving the latest base image
FROM python:latest






#Env variables
ENV RABBIT_HOST="localhost"
ENV RABBIT_PORT=5672
ENV RABBIT_USER="myuser"
ENV RABBIT_PASSWORD="mypassword"
ENV RABBIT_ALARM_QUEUE="activate_alarm"


ENV ALARM_ID="1"

ENV FLASK_RUN_HOST=0.0.0.0

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