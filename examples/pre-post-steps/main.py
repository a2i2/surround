from surround import Assembler
from stages import AddWorld, AddHello, AddSurround, AssemblerState, InputValidator

if __name__ == "__main__":
    data = AssemblerState()

    assembler = Assembler("Pre Post Example")
    assembler.set_stages([InputValidator(), AddHello(), AddWorld(), AddSurround()])
    assembler.run(data)

    print("Text is '%s'" % data.text)
