# FSOCO Tools
## Installation
Create a new Python venv with your tool of choice. We'll be using Anaconda in this brief instruction.

```shell script
# Create new environment with Python 3.7
conda create -n fsoco-tools python=3.7

# Activate created environment
conda activate fsoco-tools

# Upgrade pip to version 19.3.0 or later
pip install --upgrade pip

# Make sure you're in the tools directory, otherwise adjust the '.' path to point to it.
# Use Setuptools configuration to install tools to environment
# For usage of the CLI tools only
pip install --editable .[sly]
# For development
pip install -r requirements.txt
pre-commit install

# You've just installed the FSOCO Tools Python package
# Have a look at the Usage help with:
fsoco --help

# Have fun ;)
# As long as the venv is activated you can use the tools from wherever.
# Some of the scripts expect a default directory structure, please make sure
# to read the help tooltips before executing them or set the according options correctly.
``` 
## Development
### pre-commit hooks
You should've installed the python package via `pip install -r requirements.txt` and `pre-commit install`, and therefore have pre-commit installed.

Please bear in mind, that all modified files will be checked on each commit. If you want to keep the commit diffs minimal, remember to
commit after small changes, otherwise you'll have to commit all modified files at once or use `git stash` to temporarily hide some from pre-commit.
#### black
Formatting tool for pep8. Enforces our code style without you having to think about it too much.
#### flake8
Linter that checks if everything's according to pep8, since some stuff won't be changed by black (unused imports, etc.)
