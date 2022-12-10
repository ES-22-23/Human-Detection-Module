FROM python:latest

WORKDIR /

COPY main.py ./
COPY requirements.txt requirements.txt

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 80

CMD [ "python", "./main.py"]
