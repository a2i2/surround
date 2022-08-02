import subprocess
import time
import os
import signal
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
p = subprocess.Popen("python {}/main_wrapper.py".format(dir_path), shell=True)
time.sleep(3)
os.kill(p.pid, signal.SIGINT)
sys.exit(0)
