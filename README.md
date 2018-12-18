# Surround

Surround is a framework for serving machine learning pipelines in Python.

**Note:** Currently under heavy development.

## Intended Use Cases

* You want a flexible way to serve a pipeline in Python without writing C/C++ code for running pilot studies.
* You have multiple models (custom or pre-trained) from different frameworks that need to be combined into a single pipeline.
* You want to use existing intelligent APIs (AWS Rekognition, Google Cloud AI, Cognitive Services) as part of your pipeline.
* You have pre or post processing steps that aren't part of your models but need to be deployed as part of the pipeline.
* You need to package up your dependencies for running a pipeline offline on another machine.

## Installation

Tested on Python 2.7.15 and 3.6.5

* Clone this repository
* Navigate to the root directory
* `python3 setup.py install`

To run the tests: `python3 setup.py test`

## Usage

See the examples directory.
