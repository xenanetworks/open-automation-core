![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xoa-core) [![PyPI](https://img.shields.io/pypi/v/xoa-core)](https://pypi.python.org/pypi/xoa-core) ![GitHub](https://img.shields.io/github/license/xenanetworks/open-automation-core) [![Documentation Status](https://readthedocs.org/projects/xena-openautomation-core/badge/?version=latest)](https://xena-openautomation-core.readthedocs.io/en/latest/?badge=latest)

# Xena OpenAutomation Core
Xena OpenAutomation (XOA) Core is the framework that provides a standardized way for developers and test specialists to execute, develop, and integrate test suites, as well as managing Xena's physical and virtual Traffic Generation and Analysis (TGA) testers.

We open the source code of XOA Core to the public to empower our users with the freedom to tailor the code to their unique needs, develop and integrate their own test suites, so that XOA Core not only works with Xena-developed test suites.

All of Xena-developed test suites are in this repository: [XOA Test Suites](https://github.com/xenanetworks/open-automation-test-suites).

XOA Core uses [XOA Python API](https://github.com/xenanetworks/open-automation-python-api) as the driver to administer Xena's physical and virtual Traffic Generation and Analysis (TGA) testers.

## Documentation
The user documentation is hosted:
[Xena OpenAutomation Core Documentation](https://docs.xoa-core.xenanetworks.com/)

## Installation

### Install Using `pip`
Make sure Python `pip` is installed on you system. If you are using virtualenv, then pip is already installed into environments created by virtualenv, and using sudo is not needed. If you do not have pip installed, download this file: https://bootstrap.pypa.io/get-pip.py and run `python get-pip.py`.

To install the latest, use pip to install from pypi:
``` shell
~/> pip install xoa-core
```

To upgrade to the latest, use pip to upgrade from pypi:
``` shell
~/> pip install xoa-core --upgrade
```

> Note:
> If you install XOA Core using `pip`, XOA Python API (PyPi package name [`xoa_driver`](https://pypi.org/project/xoa-core/)) will be automatically installed.

### Install From Source Code
Make sure these packages are installed ``wheel``, ``setuptools`` on your system.

Install ``setuptools`` using pip:
``` shell
~/> pip install wheel setuptools
```

To install source of python packages:
``` shell
/xoa_core> python setup.py install
```

To build ``.whl`` file for distribution:
``` shell
/xoa_core> python setup.py bdist_wheel
```

> Note:
> If you install XOA Core from the source code, you need to install XOA Python API (PyPi package name [`xoa_driver`](https://pypi.org/project/xoa-core/)) separately. This is because XOA Python API is treated as a 3rd-party dependency of XOA Core. You can go to [XOA Python API](https://github.com/xenanetworks/open-automation-python-api) repository to learn how to install.

## Understanding XOA Core

The XOA Core is an asynchronous Python framework that can be represented by four subparts:
1. Resources Management System
2. Test Suite Plugin System
3. Test Execution System
4. Data IO System

### Resources Management System

The key functionality is represented in managing and monitoring the state of known test resources.

Under the hood, it uses the instance of [`xoa_driver`](https://pypi.org/project/xoa-core/) library as a representation of the resource. 

> Note:
> [XOA Python API](https://github.com/xenanetworks/open-automation-python-api) (PyPi package name [`xoa_driver`](https://pypi.org/project/xoa-core/)) is treated as a 3rd-party dependency, thus its source code is not included in XOA Core.

Available operations for users:
* Add testers
* Remove testers
* Connect to testers
* Disconnect from testers
* Get the list of available testers

### Test Suite Plugin System

XOA Core dynamically loads test suites that are organized in a common structure, and exposes information of those test suites to the user.

Available operations for users:
* Register plugins library
* Get the list of available test suite names
* Get test suite info by its name

Users can register one or multiple test suite lookup folders in a test script by calling the method ``register_lib(<lookup_path: str>)``.

A test suite plugin must have the structure below:

```
./my_test_suite
    |
    |- meta.yml
    |- __init__.py
    |- <any other modules defined by user>
```

``meta.yml`` has a fixed structure as shown below, and is used as the entry point for the plugin loading system. If the test suite folder doesn't contain this file, it will not be loaded by XOA Core.

``` yml
name: "RFC-2544[Frame Loss]" # Plugin name
version: "1.0" # Plugin curren version
core_version: ">=1.0.0" # compatible to xoa-core version
author: # Optional list of authors
  - "ACO"
entry_object: "FrameLossTest" # class name of script entry point
data_model: "FrameLossModel"  # class name of test suite data model
```

The ``entry_object`` must be inherited from an abstract class: ``types.PluginAbstract``

The ``data_model`` must be a class of [Pydantic](https://pydantic-docs.helpmanual.io/) model inherited from ``pydantic.BaseModel``

You can find the source code of a test suite plugin example ``./examples/billet_plugin_example/FrameLoss/``. 


> Note:
> Be aware of imports during implementation of your plugin. It is recommended to use relative import in your plugin because the library paths in different user environments can be different, which makes it impossible for the plugin code to run.

> Performance Notice:
> Test suites are treated as an ``asyncio.Task``. It means all heavy computational operations must be implemented with subprocess workers or threadings.

### Test Execution System

XOA Core provides the following controlling methods of test suite execution:

* Start test suite
* Pause/continue test suite: User should use ``await self.state_conditions.wait_if_paused()``, where the test suite should be paused/continued.
* Stop test suite: User should use ``await self.state_conditions.stop_if_stopped()``, where the test suite should be stopped.

#### Start Test Suite

Method: ``execution_id = c.start_test_suite(<plugin_name>, <suite_config_dict>)``

``<plugin_name>`` - must match the name from plugins ``meta.yml``.

``<suite_config_dict>`` - must be a dictionary matching to the following structure:

``` python
{
    "username": "JonDoe",
    "port_identities": {
        "p0": {
            "tester_id": "2906f8d041e9fd07191d6a37ef5785b2",
            "tester_index": 0,
            "module_index": 1,
            "port_index": 4
        },
        ...
    },
    "config": TestSuiteModel<as dict>
}
```

If ``test_suite`` is successfully started, the function will return an ``execution_id``, which can be used to control the test suite executions, or to subscribe to the outgoing messages from the test suite.

> Note:
> A test suite will not start if its test resources are not registered in [Resource Manager](https://xena-openautomation-python-api.readthedocs.io/en/latest/general_info.html#test-resource-management), or if one of its test resources is unavailable/disconnected.

#### Pause/Continue Test Suite

Method: ``await my_core_controller.running_test_toggle_pause(<execution_id>)``

> Note:
> To apply pause/continue action, a valid ``execution_id`` must be passed into the method.

#### Stop Test Suite

Method: ``await c.running_test_stop(<execution_id>)``.

If the execution of ``execution_id`` exists, the test suite will be terminated.


### Data IO System

XOA Core allows users to subscribe to different messages generated by different subsystems (ResourcesManager, ExecutorManager) and test suites.

Code example of message subscription:

``` python
async for msg in c.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        print(msg.dict())
```

In the snippet above, we subscribe only to the statistics messages from the test suite that is currently in execution.

The ``_filter`` argument is an set of filter types.

The first parameter of ``_filter`` argument is a mandatory identifier of the subsystem or the test suite execution.

Subsystem types:

``` python
    types.PIPE_EXECUTOR

    types.PIPE_RESOURCES
``` 

Available filters types:

``` python
class EMsgType(Enum):
    STATE = "STATE"
    DATA = "DATA"
    STATISTICS = "STATISTICS"
    PROGRESS = "PROGRESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
```

> Note:
> ``_filter`` argument is optional. If it is not provided, all message types will be returned from this test suite execution.


***

FOR TESTING BEYOND THE STANDARD.