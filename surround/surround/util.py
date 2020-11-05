import os

def generate_docker_volume_path(absolute_path):
    # If the system has a drive letter, set volume_path to /c/rest/of/path
    split_path = os.path.splitdrive(absolute_path)
    if split_path[0] != '':
        drive_letter = split_path[0][0].lower()
        path = split_path[1].replace('\\', '/')
        return '/' + drive_letter + path

    return absolute_path
