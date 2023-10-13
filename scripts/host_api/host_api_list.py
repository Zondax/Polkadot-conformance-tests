import asyncio
import websockets
import json

import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils



RPC_METHOD = "zondax_host_api"
URI = "ws://127.0.0.1:9944"

# We do not use the specs_host_api.json file 
# because the spec define functions that are not implemented 
# in polkadot, which also defines some function that are not in the 
# spec. We can go further and make a report regarding this
SPECS_HOST_API_FILE = "./scripts/host_api/specs_host_api.json"


def make_payload(method, args):
    message = utils.RpcMessage(method, args)
    return json.dumps(message.to_dict())


def runtime_host_api_msg():
    return make_payload("zondax_host_api_functions", {})

# Test to verify that Polkadot-Node provides all the host-api functions defined 
# in the specification, this will ignore any other host-api function node 
# implementors decided to add as part of their design
async def test_host_api_list(websocket):
    message = runtime_host_api_msg()
    response = await utils.send_messages(websocket, message)
    response_data = json.loads(response)
    result = response_data.get('result', '')  # Adjust this line based on the actual response format
    check_api_list(result)

def check_api_list(actual_list):
    report = {}

    with open(SPECS_HOST_API_FILE, 'r', encoding='utf-8') as file:
        base_list = json.load(file)
        # Get report on differences between lists
        report = utils.compare_lists(base_list, actual_list)
        print(json.dumps(report, indent=4))
    
    # Save report to a JSON file
    with open("host_api_report.json", "w") as file:
        json.dump(report, file, indent=4)

async def main():
    async with websockets.connect(URI) as websocket:
        await test_host_api_list(websocket)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
