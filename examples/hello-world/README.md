# Hello world example
This example shows how to print the text *"hello"* to the screen using surround.
The process consists of defining the operation in the `operate()` method of HelloStage. 
The object being processed is an instance of `BasicData`, which inherits from `SurroundData`.
The surround object is initialised with only one stage as `surround = Surround([HelloStage()]`, 
and the line `output = surround.process(BasicData())` calls the `operate()` method of `HelloStage`, 
using a new instance of BasicData as a parameter.
Finally, the content of the BasicData object is printed to screen.
## Run
From surround's root folder, run 
```bash
python3 examples/init-stage-with-data/main.py
```
