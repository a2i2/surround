from surround import Assembler
from stages import AddWorld, AddHello, AddSurround, AssemblerState, InputValidator

if __name__ == "__main__":
    data = AssemblerState()

    assembler = Assembler("Pre Post Example")
    assembler.set_validator(InputValidator())
    assembler.set_estimator(AddWorld(), [AddHello()], [AddSurround()])
    assembler.run(data)

    print("Text is '%s'" % data.text)
