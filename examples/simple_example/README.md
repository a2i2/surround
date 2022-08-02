# simple_example

## Introduction
This example is generated from the Surround CLI without the web runner support.
You can copy this project as a template for your project and use it without the CLI tool.

All CLI features can be found [here](../../surround_cli/README.md).

## Getting started
You can still use this library without the CLI support. Here is a few use cases to use it.

### Poetry
Utilising Poetry will allow you to run your project in isolation of other projects' dependencies.

You can start by installing the project dependencies defined in `pyproject.toml`
```python
$ poetry install
```

Once dependencies are installed, enable virtual env to run your project
```python
$ source `poetry env info --path`/bin/activate
```

Running your project can be done with the following command
```python
$ poetry run python -m simple_example
```

And when you are finished developing, you can exit the virtual env with this
```python
$ deactivate
```

### Doit
An alternative to run your project is by using `doit`. Firstly, you'll need to install it first if it doesn't exist.
```python
$ pip install doit==0.31.1
```

Once it is installed, you can see all available tasks by running
```python
$ doit list
```

And run the task by using
```python
$ doit <task name>
```

More information can be found [here](https://pydoit.org/)