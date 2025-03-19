# scripts
Various scripts used in the Formulae - Litterae - Chartae Project

## Recommendations:
- Create a Python virtualenv (e.g., `virtualenv --python=python3 .venv`) and use it `source .venv/bin/activate`
- If you create or run any of these scripts: aim at providing information on the execution process on every of the logging levels. Never use `print()`!

| Level | numeric value | What it means / when to use it |
|-------|---|---|
| logging.NOTSET | 0 | When set on a logger, indicates that ancestor loggers are to be consulted to determine the effective level. If that still resolves to NOTSET, then all events are logged. When set on a handler, all events are handled. |
|...|...|...|

Source: https://docs.python.org/3/library/logging.html#logging-levels

### Run a script:    
1. activate the virtualenv (e.g., `source .venv/bin/activate`) 
2. install the requirements via `pip install -r requirements.txt` within in the venv
3. If the requirements have been installed properly, you can launch `python3 <your_script>.py` 