# Template of multithread scraper with proxy update

The idea of the project is to implement a multi-threaded scraper using free proxies for requests, which will be updated and checked as the scraper is running.

## Installation:

```sh
python3.10 -m venv venv
source ./venv/bin/activate
pip install --upgrade setuptools pip
pip install poetry
poetry install
```

## Settings:

Create the `setting.py` file in the root directory of the project.

```python
# This url will be used to test proxy after proxy judge has passed.
# If the value is an empty string "", it will only be checked by proxy judge.
URL_FOR_SECOND_CHECK = ""

# Maximum number of threads for proxy checks.
MAX_WORKERS_PROXIES = 230

# Maximum number of threads for custom functions.
MAX_CUSTOM_WORKER = 0
```

In file `proxy/run_threads.py` find `custom_worker` function and implement custom code.

## Run:

```sh
python main.py
```

## Stop:

```sh
CTRL + C
```
