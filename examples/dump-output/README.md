# Dump Intermediate Output example
This example shows the use of the `dump_output()` method of the Stage class in surround by writing the outputs of two stages
(`WriteHello` and `WriteWorld`) in their respective output files.

- The surround object configuration is set in the `FileSystemRunner` class constructor, instantiated as `adapter` in *dump_output.py*.
- Through `surround.process()`, stages `PrintHello` and `PrintWorld` are executed, setting the `text` value of `BasicData` to 
 \"Hello\" and \"World\" in each stage's `operate()` method.
- Since `enable_stage_output_dump` is set to `True` in `config.yaml`, surround automatically calls the `dump_output()` 
method of each stage after `operate()`. 
- A folder stages/\<StageName\> is created for each stage, each with an `Output.txt` file, containing the value of `BasicData.text`.  
 


## Run
```bash
python3 dump_output.py -c=config.yaml
```
## Output
The output will be in the *stages/WriteHello/Output.txt* and *stages/WriteWorld/Output.txt*