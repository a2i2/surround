# File system runner example
This example takes a csv file as input, whose path is specified in the argument -f0 and extracts the word count of a
client's complaint (column 'Consumer complaint narrative').
 If specified in the config file (argument -c), the company's name (column 'Company') is extracted as well.
 The word count and (optionally) the company's name are saved in a file created in the folder specified in the -o
  (output folder) argument.

 - `CSVLoader` inherits from `Loader`. It's responsible to load your your data before it's ready to processed.

 - `CSVValidator` inherits from `Validator` will validate that `inputs` is properly loaded.

 - `AssemblerState` inherits from `State` and consists of three fields: **row_dict** (the row as read from the csv file),
 **word_count** and **company**.

 - The `assembler.run()` method calls the `estimate()` method of the stage `ProcessCSV`, where the word_count
 and company values are extracted from the row_dict field, and set on their corresponding fields in the `AssemblerState` object.

## Run
The easiest way to run the example is by running `main.py` from surround's root folder. The arguments needed are pre-set in `main.py`:
```bash
python3 examples/file-adapter/main.py
```
To use different arguments, modify `config.yaml` to set different `input` and `output` values.
