# File system runner example
This example takes a csv file as input, whose path is specified in the argument -f0 and extracts the word count of a 
client's complaint (column 'Consumer complaint narrative').
 If specified in the config file (argument -c), the company's name (column 'Company') is extracted as well.
 The word count and (optionally) the company's name are saved in a file created in the folder specified in the -o
  (output folder) argument.
 
 - The command line arguments are parsed and validated in the `FileSystemRunner` constructor (i.e., the `__init__()` method).
  The settings specified in the config file are assigned to the surround object.
  
 - The `transform()` method of the same class pre-processes the input data. In this case, the method is implemented in
  the `CustomFileSystemRunner` class to read each row of the csv file, create an instance of `BasicData`, call the 
  `surround.process()` method and save the output of all processed rows in `output.txt`.
  
 - `BasicData` inherits from `SurroundData` and consists of three fields: **row_dict** (the row as read from the csv file),
 **word_count** and **company**.

 - The `surround.process()` method calls the `operate()` method of the stage `ProcessCSV`, where the word_count 
 and company values are extracted from the row_dict field, and set on their corresponding fields in the `BasicData` object.
  
## Run
```bash
python3 file_adapter.py -f0=data/input.csv -c=config.yaml -o data/
```

