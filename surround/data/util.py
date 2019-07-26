import os
import re
import mimetypes
import hashlib
import zipfile

TYPE_FORMAT_MAPPING = {
    'Text': ['text/.*', 'application/pdf'],
    'StillImage': ['image/.*', 'application/pdf'],
    'MovingImage': ['video/.*'],
    'Dataset': ['application/vnd.ms-excel', 'application/json', 'text/csv'],
    'Sound': ['audio/.*'],
    'Collection': ['application/x-zip-compressed']
}

def get_formats_from_directory(directory):
    results = []
    for _, _, files in os.walk(directory):
        for name in files:
            guessed_type = mimetypes.guess_type(name)
            if guessed_type[0] and guessed_type[0] not in results:
                results.append(guessed_type[0])

    return results

def get_formats_from_files(files):
    formats = [t for t in [mimetypes.guess_type(name)[0] for name in files] if t is not None]
    formats = list(dict.fromkeys(formats))
    return formats

def get_types_from_formats(formats):
    types = []

    for mime in formats:
        for typ, patterns in TYPE_FORMAT_MAPPING.items():
            if any([re.match(pattern, mime) for pattern in patterns]):
                if typ not in types:
                    types.append(typ)

    return types

def prompt(question, required=True, answer_type=str, error_msg='Invalid answer, please try again!', validator=None, default=None, help_msg=None):
    if required and default:
        required = False

    while True:
        answer = input(question)

        if answer == "" and required:
            print('This field is required!')
            print()
            continue
        elif answer == "" and not required:
            print()
            return default

        if answer == "?" and help_msg:
            print(help_msg)
            print()
            continue

        if answer_type != bool:
            try:
                answer = answer_type(answer)
            except ValueError:
                print(error_msg)
                print()
                continue
        else:
            if 'y' in answer.lower() or 'n' in answer.lower():
                return answer.lower() == 'y'

            print(error_msg)
            print()
            continue

        if validator and not validator(answer):
            print(error_msg)
            print()
            continue

        print()
        return answer

def hash_file(path):
    sha1 = hashlib.sha1()
    block_size = 256 * 1024 * 1024

    with open(path, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()

def hash_zip(path, skip_files=None):
    sha1 = hashlib.sha1()
    block_size = 256 * 1024 * 1024

    with zipfile.ZipFile(path) as zipf:
        for name in zipf.namelist():
            if skip_files and name in skip_files:
                continue

            with zipf.open(name) as f:
                while True:
                    data = f.read(block_size)

                    if not data:
                        break

                    sha1.update(data)

    return sha1.hexdigest()

def split_unique(pattern, data, strip=False):
    return list({d.strip() if strip else d for d in re.split(pattern, data)})
