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

# Report abi incompatibilities
REPORT_WRONG_HOST_API = "mistmatch_host_api_report.json"

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
    # - Check the signature and ensure they are the same as in specs.

    specs_list = load_specs_list()
    node_api_list = await get_node_host_api_list(websocket)

    with open(NODE_HOST_API_FILE, 'w') as file:
        json.dump(node_api_list, file, indent=4)

    # First check that there are at least some functions defined in the specs and implemented 
    # by the node.
    report = generate_report(specs_list, node_api_list)

    # Assert that node-host-api implementation is not empty
    assert report.get('common'), "Host-api implementation does not follow specs"
    
    # Assert that impls have at least a non-empty set of methods that 
    # are defined by the official specification.
    assert report.get('common'), "Host-api implementation does not follow specs"
    
    # Save report to a JSON file
    with open(REPORT_HOST_API_LIST, 'w') as file:
        json.dump(report, file, indent=4)

    # Now check that the functions that are described in the 
    # specification are implemented in the node
    mismatch_report = check_api(specs_list, node_api_list, report['common'])

    # If there were any mismatches, save them to a report file.
    if mismatch_report:
        print("MISMATCH in lists of apis")
        with open(REPORT_WRONG_HOST_API, 'w') as file:
            json.dump(mismatch_report, file, indent=4)



def generate_report(specs, node_list):
    return utils.compare_lists([obj['name'] for obj in specs], [obj['name'] for obj in node_list])


# Will check host-api function signature follows the specification
# this will return a list with the functions that does not match.
def check_api(specs, node_list, common):
    # Lets filter out extra/missing host-api 
    # functions, and compare only the common elements.
    common_names = set(common)
    specs_common = {item['name']: item for item in specs if item['name'] in common_names}
    node_common = {item['name']: item for item in node_list if item['name'] in common_names}

    mismatch = []

    if not specs_common:
        mismatch.append({"error": "specs_common is empty", "spec": [], "node": list(node_common.values())})
    if not node_common:
        mismatch.append({"error": "node_common is empty", "spec": list(specs_common.values()), "node": []})

    if specs_common and node_common:
        for name in common_names:
            spec = specs_common.get(name)
            node = node_common.get(name)

            if spec and node:
                if spec != node:
                    mismatch.append({"spec": spec, "node": node})

    return mismatch

async def main():
    async with websockets.connect(URI) as websocket:
        await test_host_api_list(websocket)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
