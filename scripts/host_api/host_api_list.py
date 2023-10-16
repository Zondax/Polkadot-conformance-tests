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

# Save the node's list of host-api functions for reference.
NODE_HOST_API_FILE = "./scripts/host_api/node_host_api.json"

# Report file
REPORT_HOST_API_LIST = "host_api_report.json"

def make_payload(method, args):
    message = utils.RpcMessage(method, args)
    return json.dumps(message.to_dict())


def runtime_host_api_msg():
    return make_payload("zondax_host_api_functions", {})


def load_specs_list():
    specs_list = {}

    with open(SPECS_HOST_API_FILE, 'r', encoding='utf-8') as file: 
        specs_list = json.load(file)

    return specs_list

async def get_node_host_api_list(websocket):
    message = runtime_host_api_msg()

    response = await utils.send_messages(websocket, message)
    response_data = json.loads(response)

    result = response_data.get('result', '')  # Adjust this line based on the actual response format

    return result

# Test to verify that Polkadot-Node provides all the host-api functions defined 
# in the specification, this will ignore any other host-api function node 
# implementors decided to add as part of their design
async def test_host_api_list(websocket):
    # First:
    # - Get a report about the host-api functions.
    # - Check the signature and ensure they are the same as in spects.

    specs_list = load_specs_list()
    node_api_list = await get_node_host_api_list(websocket)

    with open(NODE_HOST_API_FILE, 'w') as file:
        json.dump(node_api_list, file, indent=4)

    # First check that there are at least some functions defined in the specs and implemented 
    # by the node.
    check_api_list(specs_list, node_api_list)

    # TODO: we have all we need for checking function 
    # signatures.

def check_api_list(specs, node_list):
    report = utils.compare_lists([obj['name'] for obj in specs], [obj['name'] for obj in node_list])
    
    # Assert that impls have at least a non-empty set of methods that 
    # are defined by the official specification.
    assert report.get('common'), "Host-api implementation does not follow specs"
    
    # Assert that impls have at least a non-empty set of methods that 
    # are defined by the official specification.
    assert report.get('common'), "Host-api implementation does not follow specs"
    
    # Save report to a JSON file
    with open(REPORT_HOST_API_LIST, 'w') as file:
        json.dump(report, file, indent=4)

    return report

async def main():
    async with websockets.connect(URI) as websocket:
        await test_host_api_list(websocket)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
