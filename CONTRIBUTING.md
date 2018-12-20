# Contributing to Surround

Thank you for considering contributing to Surround!


## Reporting issues

* Describe what you expected to happen.
* If possible, include a [minimal, complete, and verifiable example](https://stackoverflow.com/help/mcve) to help us identify the issue. This also helps check that the issue is not with your own code.
* Describe what actually happened. Include the full traceback if there was an exception.
* List your Python and Surround versions. If possible, check if this issue is already fixed in the repository.

## New features

* Feel free to make feature requests especially if you are willing to contribute a pull request!
* For new features, please create an issue outlining the design of the proposed feature before writing code.

## Code patches

* Include tests if your patch is supposed to solve a bug, and explain clearly under which circumstances the bug happens. Make sure the test fails without your patch.
* Try to follow PEP8, but you may ignore the line length limit if following it would make the code uglier.

### First time setup
* Download and install the [latest version of git](https://git-scm.com/downloads).

* Configure git with your [username](https://help.github.com/articles/setting-your-username-in-git/) and [email](https://help.github.com/articles/setting-your-commit-email-address-in-git/):

```
git config --global user.name 'your name'
git config --global user.email 'your email'
```

* Make sure you have a [GitHub account](https://github.com/).

* Fork Surround to your GitHub account by clicking the [Fork](https://github.com/dstil/surround/fork) button.

* [Clone](https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork) your GitHub fork locally:

```
git clone https://github.com/{username}/surround
cd surround
```

* Add the main repository as a remote to update later:

```
git remote add upstream https://github.com/dstil/surround
git fetch upstream
```

* Install Surround in editable mode with:

`pip install -e .`

### Start coding

* Create a branch and identify the issue you would like to work on.
* Using your favorite editor, make your changes, [committing as you go](https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes).
* Try to follow [PEP8](https://pep8.org/), but you may ignore the line length limit if following it would make the code uglier.
* Include tests that cover any code changes you make. Make sure the test fails without your patch. [Run the tests](#running-the-tests)
* Push your commits to GitHub and [create a pull request](https://help.github.com/articles/creating-a-pull-request/).
* Celebrate 🎉

### Running the tests

Run the basic test suite with:

`python setup.py test`

### Examples
* Make sure example works
* Make sure `main.py` class can be executed with `python main.py` so that it can be executed by the CircleCI. If your example requires parameters to run it with, make `main.py` as a wrapper to run your code.
* Add instruction of how to setup and run your example.

## Code of Conduct

Everyone interacting in the Surrond project's codebase and issue tracker is expected to follow the [PyPA Code of Conduct][coc].

[coc]: https://www.pypa.io/en/latest/code-of-conduct/
