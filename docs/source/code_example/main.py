from xoa_core import controller, types
import asyncio
import json

async def main():

    # Create a default instance of the controller class.
    my_controller = await controller.MainController()

    # Register the plugins folder.
    my_controller.register_lib("./plugins")

    # Define your tester login credentials
    my_tester_credential = types.Credentials(
        product = types.EProductType.VALKYRIE,
        host = "10.20.30.40",
        password = "xena"
        ),

    # Add tester credentials into teh controller. If already added, it will be ignored.
    # If you want to add a list of testers, you need to iterate through the list.
    await my_controller.add_tester(my_tester_credential) 

    # Subscribe to all message exchanges.
    async for msg in my_controller.listen_changes(types.PIPE_RESOURCES):
        print(msg)

    # Load your test configuration data into the test suite and run.
    with open("./my2544_data.json", "r") as f:
        data = json.load(f)
    print(my_controller.get_available_test_suites())

    execution_id = my_controller.start_test_suite("RFC-2544", data)

    # Subscribe to statistic messages.
    async for msg in my_controller.listen_changes(execution_id, _filter={types.EMsgType.STATISTICS}):
        print(msg)

if __name__ == "__main__":
    asyncio.run(main())

