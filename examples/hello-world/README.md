# Hello world example
This example shows how to print the text *"hello"* to the screen using surround.
The process consists of defining the operation in the `estimate()` method of Main.
The object being processed is an instance of `BasicData`, which inherits from `SurroundData`.
The surround object is initialised with only one stage as `assembler = Assembler(data, HelloValidator(), HelloWorld()]`,
and the line `assembler.run()` calls the `estimate()` method of `HelloWorld`,
using a new instance of BasicData as a parameter.
Finally, the content of the BasicData object is printed to screen.
## Run
From surround's root folder, run
```bash
python3 examples/hello-world/main.py
```
Or from the project's local folder:
```bash
python3 main.py
```
