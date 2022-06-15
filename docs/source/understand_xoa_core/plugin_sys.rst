.. _plugin_sys:

Test Suite Plugin System
=========================

XOA Core dynamically loads test suites that are organized in a common structure, and exposes information of those test suites to the user.

Available operations for users:
* Register plugins library
* Get the list of available test suite names
* Get test suite info by its name

Users can register one or multiple test suite lookup folders in a test script by calling the method ``register_lib(<lookup_path: str>)``.

Test Suite Plugin Folder Structure
------------------------------------

A test suite plugin must have the structure below:

::

    ./my_test_suite
        |
        |- meta.yml
        |- __init__.py
        |- <any other modules defined by user>


``meta.yml`` has a fixed structure as shown below, and is used as the entry point for the plugin loading system. If the test suite folder doesn't contain this file, it will not be loaded by XOA Core.

.. code-block:: yaml
    :caption: ``meta.yml`` example
    :linenos:

    name: "RFC-2544[Frame Loss]" # Plugin name
    version: "1.0" # Plugin curren version
    core_version: ">=1.0.0" # compatible to xoa-core version
    author: # Optional list of authors
        - "ACO"
    entry_object: "FrameLossTest" # class name of script entry point
    data_model: "FrameLossModel"  # class name of test suite data model

The ``entry_object`` must be inherited from an abstract class: ``types.PluginAbstract``

The ``data_model`` must be a class o <https://pydantic-docs.helpmanual.io/>`_ model inherited from ``pydantic.BaseModel``

.. note::

    Be aware of imports during implementation of your plugin. It is recommended to use relative import in your plugin because the library paths in different user environments can be different, which makes it impossible for the plugin code to run.

.. important::
    
    Test suites are treated as an `asyncio.Taksk <https://docs.python.org/3/library/asyncio-task.html#id2>`_ . It means all heavy computational operations must be implemented with subprocess workers or threadings.

Plugin Example
---------------

You can find the source code of a `test suite plugin example <https://github.com/xenanetworks/open-automation-core/tree/main/examples/billet_plugin_example/FrameLoss.>`_