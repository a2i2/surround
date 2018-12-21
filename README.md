# Surround

Surround is a lightweight framework for serving machine learning pipelines in Python. It is designed to be flexible, easy to use and to assist data scientists by focusing them on the problem at hand rather than writing glue code. Surround began as a project at the Applied Artificial Intelligence Institute to address the following problems:

* The same changes were required again and again to refactor code written by data scientists to make it ready for serving e.g. no standard way to run scripts, no standard way to handle configuration and no standard pipeline architecture.
* Existing model serving solutions focus on serving the model rather than serving an end-to-end solution. Our machine learning projects require multiple models and glue code to tie these models together.
* Existing serving approaches do not allow for the evolution of a machine learning pipeline without re-engineering the solution i.e. using a cloud API for the first release before training a custom model much later on.
* Code was commonly being commented out to run other branches as experimentation was not a first class citizen in the code being written.

**Note:** Surround is currently under heavy development!

## When to use Surround?

* You want a flexible way to serve a pipeline in Python without writing C/C++ code.
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

## A Simple Example

```python
from surround import Stage, PipelineData, Pipeline
import logging

class HelloStage(Stage):
    def operate(self, data, config):
        data.text = "hello"

class BasicData(PipelineData):
    text = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = Pipeline([HelloStage()])
    output = pipeline.process(BasicData())
    print(output.text)
```

## Examples

See the [examples](https://github.com/dstil/surround/tree/master/examples) directory.

### Used packages
| Package Name  | Version |
| ------------- | ------- |
| Flask         | 1.0.2   |

## Contributing

For guidance on setting up a development environment and how to make a contribution to Surround, see the [contributing guidelines](CONTRIBUTING.md).


## License

Surround is released under a [BSD-3](https://opensource.org/licenses/BSD-3-Clause) license.

## Release (only for admin)
1. Tag repo with a version that you want this to be released with.
2. Push to tag to master.
