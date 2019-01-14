# Surround Tutorial

Welcome to the Surround tutorial project!!!

## View help

`python3 -m tutorial -h`

## Run the project

`python3 -m tutorial -o data/output/ -i data/input/ -c tutorial/config.yaml`

## Project structure

<pre>
.
├── README.md
├── requirements.txt                # Python dependencies
├── docs                            # Documentation and getting started guide etc.
├── models                          # Holds trained or downloaded models (not managed by git!)
├── notebooks                       # Store Jupyter notebooks for data analysis
├── scripts                         # Miscellaneous scripts e.g. for calculating metrics
├── starter                         # Python package for the new project
│   ├── config.yaml
│   ├── __main__.py                 # Entry point for running the application
│   └── stages.py                   # Core functionality for the project starts in this module
└── data                            # Data files are stored here (not managed by git!)
    ├── input                       # Input data for the project goes here
    └── output                      # Save all files here except model files
</pre>
