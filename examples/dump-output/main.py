import subprocess

process = subprocess.Popen(['python3', 'examples/dump-output/dump_output.py', '-c=examples/dump-output/config.yaml'])
process.wait()
if not (process.returncode is None) and process.returncode > 0:
    raise Exception('Failed to run sample dump output app. Error code: ' + str(process.returncode))
