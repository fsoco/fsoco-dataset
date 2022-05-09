# FSOCO Tools

## Requirements

The FSOCO Tools are __only supported on Linux__. There is no plan to include Windows support as there are some incompatible dependencies.

The installation process is tested daily against Ubuntu 18.04, Ubuntu 20.04, and Ubuntu 22.04.

- Linux OS
- Python 3.8 (e.g., via Anaconda or virtualenv)
- GPU [optional]

## Installation
Create a new Python environment with your tool of choice. We use Conda in this brief instruction.

```shell script
# Create new environment with Python 3.8
conda create -n fsoco python=3.8

# Activate created environment
conda activate fsoco

# Upgrade pip to version 19.3.0 or later
pip install --upgrade pip

# Install setuptools version 60.8.2 as version 60.9.0 introduced a bug.
pip install setuptools==60.8.2

# Make sure you are in the tools directory, otherwise adjust the '.' path to point to it.
# Use Setuptools configuration to install tools to environment
# For usage of the CLI tools only
pip install --editable .[sly]
# For development
pip install -r requirements.txt
pre-commit install

# You have just installed the FSOCO Tools Python package
# Have a look at the usage help with (when executed the first time, this can take some seconds):
fsoco --help

# Have fun ;)
# As long as the environment is activated you can use the tools from wherever.
# Some of the scripts expect a default directory structure, please make sure
# to read the help tooltips before executing them or set the according options correctly.
``` 
## Development
### pre-commit hooks
You should have installed the python package via `pip install -r requirements.txt` and `pre-commit install`, and therefore have pre-commit installed.

Please bear in mind, that all modified files will be checked on each commit. If you want to keep the commit diffs minimal, remember to
commit after small changes, otherwise you'll have to commit all modified files at once or use `git stash` to temporarily hide some from pre-commit.
#### black
Formatting tool for pep8. Enforces our code style without you having to think about it too much.
#### flake8
Linter that checks if everything's according to pep8, since some stuff will not be changed by black (unused imports, etc.)
