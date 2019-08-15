# Initialise stage with some data example
In this example, values are loaded to a data object in each stage and printed to screen.

- In each of the two stages defined (HelloSurround and HelloWorld), the constructor initialises a variable self.data.
- In the `initialise()` method, the file with the text to be loaded is read by accessing the path set in config.yaml
for the corresponding stage, the file contents are saved in the data variable.
- In each stage's `operate()` method, the contents of the stage's data are printed to screen.

Note that although a `AssemblerState` object is initialised, it is not modified throughout this example. Instead, internal data
objects are used in each stage.
## Run
From surround's root folder, run:
```bash
python3 examples/init-stage-with-data/main.py
```

To run from the project's folder, change the paths in `main.py` and `config.yaml`, and run:
```bash
python3 main.py
```
