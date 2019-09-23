import hashlib
import zipfile

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
