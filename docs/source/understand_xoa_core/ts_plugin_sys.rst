.. _plug-in_sys:

Test Suite Plugin System
=========================

All test suites are considered plug-ins by the XOA Core. You can freely choose which test suites to use. XOA Core dynamically loads test suites that are organized in a common structure, and exposes information of those test suites to you.

**Available operations for users:**

* Register a test suite into the plug-in library
* Get the name list of available test suites
* Get test suite information by its name

Users can register one or multiple test suite lookup folders in a test script by calling the method ``register_lib(<lookup_path: str>)``.


Plugin Folder Structure
------------------------------------

A test suite plug-in must have the structure below:

::

    ./my_test_suite
        |
        |- meta.yml
        |- __init__.py
        |- <any other modules defined by user>


``meta.yml`` has a fixed structure as shown below, and is used as the entry point for the plug-in loading system. If the test suite folder doesn't contain this file, it will not be loaded by XOA Core.

.. code-block:: yaml
    :caption: ``meta.yml`` example    

    name: "RFC-2544[Frame Loss]" # Plugin name
    version: "1.0" # Plugin current version
    core_version: ">=1.0.0" # compatible to xoa-core version
    author: # Optional list of authors
        - "ACO"
    entry_object: "FrameLossTest" # class name of script entry point
    data_model: "FrameLossModel"  # class name of test suite data model

* :code:`entry_object` must be inherited from an abstract class: ``types.PluginAbstract``
* :code:`data_model` must be a class of `Pydantic <https://pydantic-docs.helpmanual.io/>`_ model inherited from ``pydantic.BaseModel``

.. note::

    Be aware of imports during implementation of your plug-in. It is recommended to use relative import in your plug-in because the library paths in different user environments can be different, which makes it impossible for the plug-in code to run.

.. important::
    
    Test suites are treated as an `asyncio.Task <https://docs.python.org/3/library/asyncio-task.html#id2>`_ . It means all heavy computational operations must be implemented with subprocess workers or threadings.

Plugin Example
---------------

We have developed a simple and executable test suite plug-in example doing RFC 2544 Frame Loss Test, and hope it help you get familiar with XOA Core.  

You can find the source code of a `test suite plug-in example <https://github.com/xenanetworks/open-automation-core/tree/main/examples/billet_plugin_example/FrameLoss>`_.