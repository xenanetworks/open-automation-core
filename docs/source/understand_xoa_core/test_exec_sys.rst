Test Execution System
======================

XOA Core provides the following controlling methods of test suite execution:

* Start test
* Pause/continue test
* Stop test

Start Test
----------

Use ``execution_id = my_core_controller.start_test_suite(<plugin_name>, <suite_config_dict>)`` to start a test and get the test ID as a returned value. With the test ID, you will be able to stop or pause the test.

    ``<plugin_name>`` - must match the name from plugin's ``meta.yml``.

    ``<suite_config_dict>`` - must be a dictionary matching to the following structure:

.. code-block:: python
    :caption: Dictionary structure for ``<suite_config_dict>``

    {
        "username": "XOA",
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


If the test suite is successfully started, the function ``start_test_suite`` will return an ``execution_id``, which can be used to control the test suite executions, or to subscribe to the outgoing messages from the test suite.

.. note::
    
    A test suite will not start if its test resources are not registered in :term:`Resource Manager`, or if one of its test resources is unavailable/disconnected.


Pause/Continue Test
-------------------

Use ``await my_core_controller.running_test_toggle_pause(<execution_id>)`` to pause/continue a test.

User should use ``await self.state_conditions.wait_if_paused()``, where the test suite should be paused/continued.

.. note::
    
    To apply pause/continue action, a valid ``execution_id`` must be passed into the method.


Stop Test
---------

Use ``await my_core_controller.running_test_stop(<execution_id>)`` to stop a test.

User should use ``await self.state_conditions.stop_if_stopped()``, where the test suite should be stopped.

If the execution of ``execution_id`` exists, the test suite will be terminated.
