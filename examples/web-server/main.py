import time
import subprocess


process = subprocess.Popen(['python3', 'examples/web-server/sample_web_service.py'])
time.sleep(5)
process.terminate()
process.poll()
if not (process.returncode is None) and process.returncode > 0:
    raise Exception('Failed to run sample web service app. Error code: ' + str(process.returncode))
