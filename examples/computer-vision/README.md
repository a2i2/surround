### Example for a Computer Vision pipeline

Apply a set of image processing operations or an inference 
algorithm to either a set of images or the frames of a video. 
Particular examples of this set of problems include:
* Image Classification
* Object Detection
* Face Location and Recognition
* Other?

This simple example uses the video stream from the webcam 
to implement an inference algorithm within the capabilities 
of surround.

To execute this example simply execute within this directory
```bash
make
```
which is equivalent with
```bash
python main.py
```

### Development and dependencies
* OS: MacOSX/Unix 
* Python package manager: Anaconda
* conda version: 4.4.10
* python version: 3.6.5

To install the `opencv` library for image and video 
manipulation:
```bash
pip install opencv-python==3.4.5.20
```