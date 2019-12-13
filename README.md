# excode

<!-- [![CircleCI](https://img.shields.io/circleci/project/github/nschloe/excode/master.svg)](https://circleci.com/gh/nschloe/excode)
[![codecov](https://codecov.io/gh/nschloe/excode/branch/master/graph/badge.svg)](https://codecov.io/gh/nschloe/excode)
[![PyPi Version](https://img.shields.io/pypi/v/excode.svg)](https://pypi.python.org/pypi/excode)
[![GitHub stars](https://img.shields.io/github/stars/sharm294/excode.svg?logo=github&label=Stars)](https://github.com/sharm294/excode) -->

This is excode, a tool for extracting code blocks from markdown files.

For example, the command
```
excode ./ ./tests/
```
takes all markdown files in the local directory (which let's say only contains a file named `input.md`),
````
[//]: # (excode-config: mode=python)
Lorem ipsum
```python
add = 1 + 2 + 3
print(add)
```
````
and creates `input.py` and places it in the `./tests/` directory,
```python
def test_0():
    add = 1 + 2 + 3
    print(add)
    return
```
This can be used for automatically turning snippets from markdown files into testable code that can be tested using pytest.
Note that `[//]: # (...)` is a non-rendering/printing Markdown comment that's used to enable excode on a particular file and provide some control features.

## Installation

The original excode is [available on PyPI](https://pypi.python.org/pypi/excode/).
If these [changes](#differences-from-the-original-project) are merged into the this package, then it can be installed/upgraded with:
```
pip install -U excode
```

Otherwise, clone this repository and run

```
pip install .
```
to install the package using the cloned repository.

## Testing

To run the unit tests, clone this repository and run
```
pytest
```

## Differences from the Original Project

* Support shell and python blocks in Markdown
* Run on directories instead of just single files
* Use Markdown comments for configuration and controlling code generation

## License

excode is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
