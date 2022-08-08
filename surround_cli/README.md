<p align="center">
    <img src="../docs/source/temp_logo_hq.png" width="500">
</p>

# Surround CLI

Surround CLI comes with a range of command line tools to help you create and run Surround pipelines.

To get more information on these tools, run the following command:
```
$ surround -h
```

## Installation

### Prerequisites
- [Python](https://www.python.org/) 3+ (Tested on 3.6.5)
- [Docker](https://www.docker.com/) (required for running in containers)
- [Tornado](https://www.tornadoweb.org/en/stable/) (optional, needed if serving via Web)

Use package manager [pip](https://pip.pypa.io/en/stable/) to install the latest (stable) version:
```
$ pip3 install surround_cli
```

### Generating projects
For example you can use the sub-command ``init`` to generate a new project:
```
$ surround init <path-to-dir> --project-name sample --description "Sample description" --author-name <AUTHOR_NAME> --author-email <AUTHOR_EMAIL> --require-web <True/False>
```

Where a new folder in `path-to-dir` (current directory if left blank) will be created with the name of the project. In this folder will be a collection of scripts and folders typically needed for a Surround project. For more information on what is generated, see our [Getting Started](https://surround.readthedocs.io/getting-started.html) guide.

### Running projects
You can then test the genereated pipeline using the `run` sub-command in the root of the project like so:
```
$ surround run batchLocal
```

This will execute the pipeline locally in batch mode. If you want to run the pipeline in a container then use the following:
```
$ surround run build
$ surround run batch
```

If you would like to serve your pipeline via Web endpoints (`--require-web` is required when generating for this option) then you can use:
```
$ surround run web
```
Which (by default) will accept input data as JSON via HTTP POST to the endpoint `http://localhost:8081/estimate` in the following format:
```
{ "message": "this data will be processed by the pipeline" }
```

To see a full list of the available tasks just run the following command:
```
$ surround run
```

For more information on different run modes and when/how they should be used see both our [About](https://surround.readthedocs.io/en/latest/about/) and [Getting Started](https://surround.readthedocs.io/en/latest/getting-started/#) pages.
