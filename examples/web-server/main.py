import time
import subprocess


process = subprocess.Popen(['python', 'examples/web-server/sample_web_service.py'])
time.sleep(5)
process.terminate()
process.poll()
if process.returncode != None and process.returncode > 0:
    raise Exception('Failed to run sampe web service app. Error code: ' + str(process.returncode))
