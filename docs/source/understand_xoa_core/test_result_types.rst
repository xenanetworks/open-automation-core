Test Result Types
=================

XOA Core sends test result data (in json format) to your code as shown in the example below. It is up to you to decide how to process them, either `parse JSON into Python dictionary <https://docs.python.org/3/library/json.html>`_, display in your console, or store them into a file.

.. code-block:: python
    :caption: Receive test result data

    async for stats_data in ctrl.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        print(stats_data)


There are three types of test result data (JSON format) that you receive from XOA Core. 

* Live test result data

Every second, XOA queries statistics such as port TX and RX counters and sends them to you. The amount of this type of test result data can be large when your test duration is long.

* Intermediate test result data

If the test uses an iterative searching algorithm, such binary search in RFC 2544 Throughput Test and Back-to-Back Test, the result data after each searching step is called intermediate result because the searching is not yet complete. Intermediate results let you keep track of the searching steps.

* Final test result data

Final result date are the conclusion of a certain test iteration. For example, the throughput value for a certain frame size, the traffic latency value for a certain traffic rate with a certain frame size. This type of test result lets you analyze and verify the performance, conformance, and functionalities of your DUT/SUT.


To check the type of the test result data:

.. code-block:: python
    :caption: Check the type of the test result data

    # The example here only shows a print of test result data.
    async for stats_data in ctrl.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        if stats_data.is_final == True:
            # This is final result
        else:
            ...
