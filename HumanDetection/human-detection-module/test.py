import requests

obj = {"cameraId":1, "timestamp":"2022-11-21 11:50:24.537430"}
intrusionAPI_url = "http://localhost:8083/intrusion"
x = requests.post(intrusionAPI_url, json = obj)
print("nice")