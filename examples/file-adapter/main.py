import subprocess

process = subprocess.Popen(['python', 'examples/file-adapter/file_adapter.py', '-f0=examples/file-adapter/data/input.csv', '-c=examples/file-adapter/config.yaml', '-o', 'examples/file-adapter/data/'])
process.wait()
if not (process.returncode is None) and process.returncode > 0:
    raise Exception('Failed to run sampe file adapter app. Error code: ' + str(process.returncode))
