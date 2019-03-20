import json
import base64
import requests
from surround import Stage, SurroundData

class CarData(SurroundData):
    output_data = None

    def __init__(self, input_data):
        self.input_data = input_data

class DetectCar(Stage):
    def operate(self, surround_data, config):
        self.send_curl_request(surround_data)

    def encode_image(self, path):
        with open(path, "rb") as image_file:
            image_content = image_file.read()
            return base64.b64encode(image_content)

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

        content = self.read_text_file(surround_data.input_data)

        data = {'requests' : [{'image': {'content': content}, 'features' : features}]}

        vision_base_url = "https://vision.googleapis.com/v1/images:annotate"
        ocr_url = vision_base_url + "?key=" + key

        response = requests.post(
            ocr_url, headers=headers, data=json.dumps(data))

        surround_data.output_data = response.json()
