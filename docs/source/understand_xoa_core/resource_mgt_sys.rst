.. _resource_mgt_sys:

Resources Management System
================================

The key functionality is represented in managing and monitoring the state of known testers.

**Available operations for users:**

* Add testers
* Remove testers
* Connect to testers
* Disconnect from testers
* Get the list of available testers

You can find the corresponding APIs in :doc:`../api_ref/index`

Under the hood, XOA Core uses the instance of `xoa_driver <https://pypi.org/project/xoa-driver/>`_ library as a representation of the resource. 

.. note::

    `XOA Python API <https://github.com/xenanetworks/open-automation-python-api>`_ (PyPI package name `xoa_driver <https://pypi.org/project/xoa-driver/>`_) is treated as a 3rd-party dependency, thus its source code is not included in XOA Core.