![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xoa-core) [![PyPI](https://img.shields.io/pypi/v/xoa-core)](https://pypi.python.org/pypi/xoa-core) ![GitHub](https://img.shields.io/github/license/xenadevel/xena-open-automation-core)
# Xena OpenAutomation Core
Xena OpenAutomation (XOA) Core is the framework for managing testing resources and executing different test suites.


## Framework Architecture
![xoa-core Diagram](./diagrams/xoa-core.jpg)


## Description

The XOA Core is an asynchronous Python library that can be represented by 4 subparts:
1. Resources Management System
2. Test Suite Plugin System
3. Test Execution System
4. Data IO System

### 1. Resources Management System

The key functionality is represented in managing and monitoring the state of known testing resources.
Under the hood, it uses the instance of [`xoa_driver`](https://pypi.org/project/xoa-driver/) The library as a representation of the resource. 

> Note:
> [XOA Python API library](https://github.com/xenadevel/xena-open-automation-python-api) (PyPi package name [`xoa_driver`](https://pypi.org/project/xoa-driver/)) is treated as a 3rd party dependency, of which the source code is not included in to XOA Core.

#### Use Case Description


### 2. Test Suite Function Factory
// TODO


### 3. Test Suite Plugin System
// TODO


### 4. Test Execution System
// TODO
