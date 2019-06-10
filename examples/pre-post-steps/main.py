from surround import Assembler
from stages import AddWorld, AddHello, AddSurround, BasicData, ValidateData

if __name__ == "__main__":
    data = BasicData()

    assembler = Assembler("Pre Post Example", ValidateData())
    assembler.set_estimator(AddWorld(), [AddHello()], [AddSurround()])
    assembler.run(data)

    print("Text is '%s'" % data.text)
