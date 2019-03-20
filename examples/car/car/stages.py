import json
import subprocess
import requests
import cv2
import numpy as np
from surround import Stage, SurroundData

class CarData(SurroundData):
    output_data = None

    def __init__(self, input_data):
        self.input_data = input_data

class EncodeImage(Stage):
    def operate(self, surround_data, config):
        with open("data/temp.jpg", "wb")  as outfile:
            outfile.write(surround_data.input_data)

        surround_data.input_data = "data/temp.jpg"
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

class ExtractCar(Stage):
    def operate(self, surround_data, config):
        self.crop_image(surround_data)

    def crop_image(self, surround_data):
        # Read a image
        I = cv2.imread('data/temp.jpg')

        # Get Image size
        height, width = I.shape[:2]

        # Define the polygon coordinates to use or the crop
        polygon = [[[20,110],[450,108],[340,420],[125,420]]]

        # First find the minX minY maxX and maxY of the polygon
        minX = I.shape[1]
        maxX = -1
        minY = I.shape[0]
        maxY = -1
        for point in polygon[0]:

            x = point[0]
            y = point[1]

            if x < minX:
                minX = x
            if x > maxX:
                maxX = x
            if y < minY:
                minY = y
            if y > maxY:
                maxY = y

        # Go over the points in the image if they are outside of the enclosing rectangle put zero
        # if not check if they are inside the polygon or not
        croppedImage = np.zeros_like(I)
        for y in range(0,I.shape[0]):
            for x in range(0, I.shape[1]):

                if x < minX or x > maxX or y < minY or y > maxY:
                    continue

                if cv2.pointPolygonTest(np.asarray(polygon),(x,y),False) >= 0:
                    croppedImage[y, x, 0] = I[y, x, 0]
                    croppedImage[y, x, 1] = I[y, x, 1]
                    croppedImage[y, x, 2] = I[y, x, 2]

        # Now we can crop again just the envloping rectangle
        finalImage = croppedImage[minY:maxY,minX:maxX]

        cv2.imwrite('data/temp.jpg',finalImage)
