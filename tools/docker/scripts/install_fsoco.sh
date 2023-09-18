python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install setuptools==60.8.2
python -m pip install -e .[sly]
