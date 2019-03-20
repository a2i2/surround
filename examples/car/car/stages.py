import os
import json
import subprocess
import requests
import cv2
import numpy as np
from surround import Stage, SurroundData

KEY = "Your API Key"

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
        headers = {
            'Content-Type': 'application/json',
            'charset': 'utf-8'
        }

        features = [{'type': 'OBJECT_LOCALIZATION'}]

        content = str(surround_data.input_data)

        data = {'requests' : [{'image': {'content': content}, 'features' : features}]}

        vision_base_url = "https://vision.googleapis.com/v1/images:annotate"
        ocr_url = vision_base_url + "?key=" + KEY

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

        response = surround_data.output_data.get('responses', "error")

        if response == "error":
            print("Response is not correct, Your API Key is probably incorrect")
        else:
            localized_object_annotations = response[0]['localizedObjectAnnotations']

            for idx, localized_object_annotation in enumerate(localized_object_annotations):
                coordinates = localized_object_annotation['boundingPoly']['normalizedVertices']

                point_1 = [round(coordinates[0].get('x', 0)*width), round(coordinates[0].get('y', 0)*height)]
                point_2 = [round(coordinates[1].get('x', 0)*width), round(coordinates[1].get('y', 0)*height)]
                point_3 = [round(coordinates[2].get('x', 0)*width), round(coordinates[2].get('y', 0)*height)]
                point_4 = [round(coordinates[3].get('x', 0)*width), round(coordinates[3].get('y', 0)*height)]

                # Define the polygon coordinates to use or the crop
                polygon = [[point_1, point_2, point_3, point_4]]

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

                        if cv2.pointPolygonTest(np.asarray(polygon), (x, y), False) >= 0:
                            croppedImage[y, x, 0] = I[y, x, 0]
                            croppedImage[y, x, 1] = I[y, x, 1]
                            croppedImage[y, x, 2] = I[y, x, 2]

                finalImage = croppedImage[minY:maxY, minX:maxX]

                cv2.imwrite('data/ExtractCar/' + str(idx) + '.jpg', finalImage)

class ReadNumberPlate(Stage):
    def operate(self, surround_data, config):
        for file_ in os.listdir("data/ExtractCar"):
            if file_ != ".gitignore":
                print('data/ExtractCar/' + file_)
                self.send_curl_request(surround_data, 'data/ExtractCar/' + file_)

    def read_text_file(self, path):
        with open(path, "r") as text_file:
            return text_file.read()

    def encode_image(self, path):
        encoded_image = subprocess.run(['base64', '-i', path], encoding='utf-8', stdout=subprocess.PIPE)
        return encoded_image

    def send_curl_request(self, surround_data, path):
        headers = {
            'Content-Type': 'application/json',
            'charset': 'utf-8'
        }

        features = [{'type': 'DOCUMENT_TEXT_DETECTION'}]

        encoded_image = self.encode_image(path)
        surround_data.input_data = encoded_image.stdout

        content = str(surround_data.input_data)

        data = {'requests' : [{'image': {'content': content}, 'features' : features}]}

        vision_base_url = "https://vision.googleapis.com/v1/images:annotate"
        ocr_url = vision_base_url + "?key=" + KEY

        response = requests.post(
            ocr_url, headers=headers, data=json.dumps(data))

        surround_data.output_data = response.json()
        response = surround_data.output_data.get('responses', "error")
        if response == "error":
            print("Response is not correct, Your API Key is probably incorrect")
        else:
            description = response[0]['textAnnotations'][0]['description']
            print(description)
