from surround import Assembler
from stages import AddWorld, AddHello, AddSurround, BasicData

if __name__ == "__main__":
    data = BasicData()

    assembler = Assembler("Pre Post Example", data)
    assembler.set_estimator(AddWorld(), [AddHello()], [AddSurround()])
    assembler.run()

    print("Text is '%s'" % data.text)
