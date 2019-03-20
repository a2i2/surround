import json
import subprocess
import requests
from surround import Stage, SurroundData

class CarData(SurroundData):
    output_data = None

    def __init__(self, input_data):
        self.input_data = input_data

class EncodeImage(Stage):
    def operate(self, surround_data, config):
        encoded_image = self.encode_image(surround_data)
        surround_data.input_data = encoded_image.stdout

    def encode_image(self, surround_data):
        encoded_image = subprocess.run(['base64', '-i', surround_data.input_data], encoding='utf-8', stdout=subprocess.PIPE)
        return encoded_image

class DetectCar(Stage):
    def operate(self, surround_data, config):
        self.send_curl_request(surround_data)

    def read_text_file(self, path):
        with open(path, "r") as text_file:
            return text_file.read()

    def send_curl_request(self, surround_data):
        key = "Your API Key"

        headers = {
            'Content-Type': 'application/json',
            'charset': 'utf-8'
        }

        features = [{'type': 'OBJECT_LOCALIZATION'}]

        content = str(surround_data.input_data)

        data = {'requests' : [{'image': {'content': content}, 'features' : features}]}

        vision_base_url = "https://vision.googleapis.com/v1/images:annotate"
        ocr_url = vision_base_url + "?key=" + key

        response = requests.post(
            ocr_url, headers=headers, data=json.dumps(data))

        surround_data.output_data = response.json()
