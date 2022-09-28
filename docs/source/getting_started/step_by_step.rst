Step-by-Step Guide
===================

This section provides a step-by-step guide on how to use XOA Core to run XOA test suites. It covers topics such as:

* **Setup your XOA test suite project**

  * `Step 1. Create Project Folder`_
  * `Step 2. Create Necessary Files`_
  * `Step 3. Install XOA Core`_

* **Where should XOA test suite plug-ins be placed**

  * `Step 4. Copy XOA Test Suite Plugin into Project Folder`_

* **How to configure a XOA test suite**

  * `Step 5. Write Your Code in main.py`_

* **How to fetch the outgoing statistics data**

  * `Step 5. Write Your Code in main.py`_


Step 1. Create Project Folder
------------------------------

First, create a folder on your computer at a location you want. This folder will be the place where you keep your XOA test suites and a simple Python program to load and run them using XOA Core framework.

Let's create a folder called ``/my_xoa_project``

.. code-block::
    :caption: Create project folder

    /my_xoa_project
        |


Step 2. Create Necessary Files
--------------------------------

Create a ``main.py`` file inside the folder ``/my_xoa_project``.

Then, on the same level as ``main.py``, create a folder ``/plugins`` for keeping your test suites.

After that, create a ``__init__.py`` inside folder ``/plugins`` to make it into a `package <https://docs.python.org/3/tutorial/modules.html#packages>`_.

.. code-block::
    :caption: Create necessary files

    /my_xoa_project
        |
        |- main.py
        |- /plugins
            |- __init__.py
            |


Step 3. Install XOA Core
-------------------------

If you have already installed XOA Core in your system, either to your global namespace or in a virtual environment, you can skip this step.

Else, read :doc:`installation`.


Step 4. Copy XOA Test Suite Plugin into Project Folder
-------------------------------------------------------

Copy a test suite plugin, e.g. ``/plugin2544`` from `XOA Test Suite <https://github.com/XenaNetworks/open-automation-test-suites>`_ into ``/my_xoa_project/plugins``.

Copy your test configuration ``json`` file, e.g. ``my2544_data.json`` into ``/my_xoa_project`` for easy access.

.. code-block::
    :caption: Copy test suite plugin into project

    /my_xoa_project
        |
        |- main.py
        |- my2544_data.json
        |- /plugins
            |- __init__.py
            |- /plugin2544


Step 5. Write Your Code in ``main.py``
--------------------------------------

The code example in ``main.py`` below demonstrates a very basic flow. 

.. literalinclude:: ../code_example/main.py
    :language: python


To execute the program, simply do:

.. tab:: Windows
    :new-set:

    .. code-block:: doscon
        :caption: Run test suite in Windows.

        [my_xoa_project]> python main.py

.. tab:: macOS/Linux

    .. code-block:: console
        :caption: Run test suite in macOS/Linux.

        [my_xoa_project]$ python3 main.py
