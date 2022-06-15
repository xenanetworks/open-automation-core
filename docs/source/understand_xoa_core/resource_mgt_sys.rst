.. _resource_mgt_sys:

Resources Management System
============================

The key functionality is represented in managing and monitoring the state of known test resources.

Under the hood, it uses the instance of `xoa_driver <https://pypi.org/project/xoa-core/>`_ library as a representation of the resource. 

.. note::

    `XOA Python API <https://github.com/xenanetworks/open-automation-python-api>`_ (PyPi package name `xoa_driver <https://pypi.org/project/xoa-core/>`_) is treated as a 3rd-party dependency, thus its source code is not included in XOA Core.

Available operations for users:
* Add testers
* Remove testers
* Connect to testers
* Disconnect from testers
* Get the list of available testers