from threading import Timer
import os
import sys


def exit():
    sys.exit(0)

t = Timer(5.0, exit)
t.start()

os.system('python examples/web-server/sample_web_service.py &')
