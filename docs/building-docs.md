# Building the documentation using Sphinx

## Dependencies
Install the dependencies listed in `docs/requirements.txt` using PIP:
```
$ pip3 install -r requirements.txt
```

## Building HTML
Use `sphinx-build` to render the documents as HTML:
```
$ sphinx-build source/ source/_build
```

This will place all of the HTML files in `docs/source/_build`.

**NOTE**: `_build` is ignored by Git.