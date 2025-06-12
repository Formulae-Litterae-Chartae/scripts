# scripts

Various scripts used in the Formulae - Litterae - Chartae Project

## Recommendations:

- Create a Python virtualenv (e.g., `virtualenv --python=python3 .venv`) and use it `source .venv/bin/activate`
- If you create or run any of these scripts: aim at providing information on the execution process on every of the logging levels. Never use `print()`!

| Level            | numeric value | What it means / when to use it                                                                                                                                                                                           |
| ---------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| logging.NOTSET   | 0             | When set on a logger, indicates that ancestor loggers are to be consulted to determine the effective level. If that still resolves to NOTSET, then all events are logged. When set on a handler, all events are handled. |
| logging.DEBUG    | 10            | Detailed information, typically only of interest to a developer trying to diagnose a problem.                                                                                                                            |
| logging.INFO     | 20            | Confirmation that things are working as expected.                                                                                                                                                                        |
| logging.WARNING  | 30            | An indication that something unexpected happened, or that a problem might occur in the near future (e.g. ‘disk space low’). The software is still working as expected.                                                 |
| logging.ERROR    | 40            | Due to a more serious problem, the software has not been able to perform some function.                                                                                                                                  |
| logging.CRITICAL | 50            | A serious error, indicating that the program itself may be unable to continue running.                                                                                                                                   |

Source: https://docs.python.org/3/library/logging.html#logging-levels

### Run a script:

1. activate the virtualenv (e.g., `source .venv/bin/activate`)
2. install the requirements via `pip install -r requirements.txt` within in the venv
3. If the requirements have been installed properly, you can launch `python3 <your_script>.py`

#### transform_cte_to_dll

```shell
cd ~/git/scripts/formel_transform/output/sens
python3 ~/git/scripts/corpus_transformation_scripts/Formulae/transform_cte_to_dll.py ~/Downloads/SaxonHE9-8-0-11J/saxon9he.jar sens ~/git/formulae-corpora/data/formulae_collection/__capitains__.xml ~/git/scripts 
```

## Contribution guide
This collection of scripts consists of Python and xslt files.
### Python style guide and documentation
In the future, all public repositories of the project could benefit from a SPHINX documentation to encourage the re-usability by others.
There I decided the following documentation style guide for python code:

1. Use type hints as in [PEP484](https://peps.python.org/pep-0484/): `def func_pep484_annotations(param1: int) -> bool`
2. `import`-statements should be at the top of a file. Never within classes or methods.
3. One class per file
4. Prefer logging over print
5. If not further specified specified, stick to https://google.github.io/styleguide/pyguide.html
6. Use `match-case` [PEP634](https://docs.python.org/3.10/whatsnew/3.10.html#pep-634-structural-pattern-matching) when possible.
### XSLT programming
Always restart your terminal when changing xslt-files. Otherwise the terminal uses a cached version.