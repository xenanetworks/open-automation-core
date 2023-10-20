![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xoa-core) [![PyPI](https://img.shields.io/pypi/v/xoa-core)](https://pypi.python.org/pypi/xoa-core) ![GitHub](https://img.shields.io/github/license/xenanetworks/open-automation-core) [![Documentation Status](https://readthedocs.com/projects/xena-networks-open-automation-core/badge/?version=latest)](https://docs.xenanetworks.com/projects/xoa-core/en/latest/?badge=latest)

# Xena OpenAutomation Test Suite - Core
Xena OpenAutomation Core (XOA Core) is an open-source test suite framework for network automation and testing. It is designed to host various [XOA Test Suites](https://github.com/xenanetworks/open-automation-test-suites) as plugins, allowing users to create, manage, and run test cases for different network scenarios. The XOA Core framework serves as the foundation for building and executing test suites in the XOA ecosystem.

Key features of XOA Core include:

1. Modular architecture: The test suite framework employs a modular architecture, enabling users to develop and run different test suites as plugins.

2. Test Suite execution: XOA Core supports both local and remote test suite execution. Users can execute test suites on their local machines or on remote testbeds through the XOA CLI or Web GUI.

3. Test Case management: XOA Core provides tools for managing test cases, including creating, updating, and deleting them. Users can also organize test cases using tags and execute them in parallel or sequentially.

4. Extensibility: The framework is designed to be extensible, allowing users to develop custom test suites and plugins to address specific testing requirements.

5. Logging and reporting: XOA Core offers built-in logging and reporting functionality, generating detailed test reports to help users analyze test results and identify issues.
Xena OpenAutomation (XOA) Core is the framework that provides a standardized way for developers and test specialists to execute, develop, and integrate test suites, as well as managing Xena's physical and virtual Traffic Generation and Analysis (TGA) testers.

## Documentation
The user documentation is hosted:
[Xena OpenAutomation Core Documentation](https://docs.xenanetworks.com/projects/xoa-core)


## Step-by-Step

This section provides a step-by-step guide on how to use XOA Core to run XOA test suites. 

### Create Project Folder

To run XOA test suites, you need a folder to place the test suite plugins, the test configuration files, and yous Python script to control the tests.

Let's create a folder called ```/my_xoa_project```

```
/my_xoa_project
    |
```

### Install XOA Core and XOA Converter


After creating the folder, install ```xoa-core``` and ```xoa-converter```using pip:

```
pip install xoa-core -U
pip install xoa-converter -U
```

### Place Test Suite Plugins

Place the corresponding [XOA RFC test suite plugins](https://github.com/xenanetworks/open-automation-rfc-test-suites) and the test configuration files in ```/my_xoa_project```.

Your project folder will look like this afterwards.

```
/my_xoa_project
    |
    |- /test_suites
        |- /plugin2544
        |- /plugin2889
        |- /plugin3918
```


### Run Tests from Valkyrie RFC Test Suite Configurations

> Read more about [XOA Config Convert](https://docs.xenanetworks.com/projects/xoa-config-converter)

Copy your Valkyrie test configurations into ```/my_xoa_project``` for easy access. Then create a ```main.py``` file inside the folder ```/my_xoa_project```.

```
/my_xoa_project
    |
    |- main.py
    |- old_2544_config.v2544
    |- old_2889_config.v2889
    |- old_3918_config.v3918
    |- /test_suites
        |- /plugin2544
        |- /plugin2889
        |- /plugin3918
```

This ```main.py``` controls the test workflow, i.e. load the configuration files, start tests, receive test results, and stop tests. The example below demonstrates a basic flow for you to run XOA tests.


``` python
from __future__ import annotations
import sys
from xoa_core import (
    controller,
    types,
)
import asyncio
import json
from pathlib import Path
# XOA Converter is an independent module and it needs to be installed via `pip install xoa-converter`
try:
    from xoa_converter.entry import converter
    from xoa_converter.types import TestSuiteType
except ImportError:
    print("XOA Converter is an independent module and it needs to be installed via `pip install xoa-converter`")
    sys.exit()

PROJECT_PATH = Path(__file__).parent
OLD_2544_CONFIG = PROJECT_PATH / "old_2544_config.v2544"
OLD_2889_CONFIG = PROJECT_PATH / "old_2889_config.v2889"
PLUGINS_PATH = PROJECT_PATH / "test_suites"


async def subscribe(ctrl: "controller.MainController", channel_name: str, fltr: set["types.EMsgType"] | None = None) -> None:
    async for msg in ctrl.listen_changes(channel_name, _filter=fltr):
        print(msg)



async def main() -> None:
    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product=types.EProductType.VALKYRIE,
        host="10.20.30.40"
    )

    # Create a default instance of the controller class.
    ctrl = await controller.MainController()

    # Register the plugins folder.
    ctrl.register_lib(str(PLUGINS_PATH))

    # Add tester credentials into teh controller. If already added, it will be ignored.
    # If you want to add a list of testers, you need to iterate through the list.
    await ctrl.add_tester(my_tester_credential)

    # Subscribe to test resource notifications.
    asyncio.create_task(subscribe(ctrl, channel_name=types.PIPE_RESOURCES))

    # Convert Valkyrie 2544 config into XOA 2544 config and run.
    with open(OLD_2544_CONFIG, "r") as f:
        # get rfc2544 test suite information from the core's registration
        info = ctrl.get_test_suite_info("RFC-2544")
        if not info:
            print("Test suite is not recognized.")
            return None

        # convert the old config file into new config file
        new_data = converter(TestSuiteType.RFC2544, f.read())

        # you can use the config file below to start the test
        new_config = json.loads(new_data)

        # Test suite name: "RFC-2544" is received from call of c.get_available_test_suites()
        execution_id = ctrl.start_test_suite("RFC-2544", new_config)


        # The example here only shows a print of test result data.
        asyncio.create_task(
            subscribe(ctrl, channel_name=execution_id, fltr={types.EMsgType.STATISTICS})
        )

    # By the next line, we prevent the script from being immediately
    # terminated as the test execution and subscription are non blockable, and they ran asynchronously,
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

```


### Receive Test Result Data

XOA Core sends test result data (in JSON format) to your code as shown in the example below. It is up to you to decide how to process it, either parse it and display in your console, or store them into a file.

> Read about [Test Result Types](https://docs.xenanetworks.com/projects/xoa-core/en/latest/understand_xoa_core/test_result_types.html)


***

FOR TESTING BEYOND THE STANDARD.
