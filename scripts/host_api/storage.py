import asyncio
import websockets
import json

import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

STORAGE_SET = "ZondaxTest_set_storage"
STORAGE_GET = "ZondaxTest_get_storage"
STORAGE_CLEAR = "ZondaxTest_clear_storage"

RPC_METHOD = "zondax_host_api"
URI = "ws://127.0.0.1:9944"

# TODO: Add more value types, for this we would 
# need to improve the scale encode/decode helper functions
TEST_DATA = {
    "key1": "key1_value",
    "key2": "key2_value",
    "key3": "key3_value", 
    "key1": "value_changed"
}


async def check_storage_set_get(websocket, test_data):
    for key, value in test_data.items():

        args = utils.scale_encode([key.encode('utf8'), value.encode('utf8')], 'Vec<Bytes>')

        msg = utils.host_api_msg(STORAGE_SET, args)

        response = await utils.send_messages(websocket, msg)
        response_data = json.loads(response)
        result = response_data.get('result', '')

        assert result == [], "Expected result to be an empty list, but it was not."

        args = utils.scale_encode([key.encode('utf8')], 'Vec<Bytes>')

        msg = utils.host_api_msg(STORAGE_GET, args)

        response = await utils.send_messages(websocket, msg)
        response_data = json.loads(response)

        result = response_data.get('result', '')

        result = utils.scale_decode(result, 'Option<Bytes>')

        assert result == value, f"Unexpected storage value: {result} for original value: {value}"

    return

async def check_storage_clear(websocket, test_data):
    for key, value in test_data.items():
        args = utils.scale_encode([key.encode('utf8')], 'Vec<Bytes>')

        msg = utils.host_api_msg(STORAGE_CLEAR, args)

        response = await utils.send_messages(websocket, msg)
        response_data = json.loads(response)

        result = response_data.get('result', '')

        assert result == [], "Expected result to be an empty list, but it was not."

        # Now try to get the value after and assert it is empty
        args = utils.scale_encode([key.encode('utf8')], 'Vec<Bytes>')

        msg = utils.host_api_msg(STORAGE_GET, args)

        response = await utils.send_messages(websocket, msg)
        response_data = json.loads(response)

        result = response_data.get('result', '')
        result = utils.scale_decode(result, 'Option<Bytes>')

        assert result == None, f"Unexpected storage value"



async def main():
    async with websockets.connect(URI) as websocket:
        await check_storage_set_get(websocket, TEST_DATA)
        print("\n Clearing storage \n")
        await check_storage_clear(websocket, TEST_DATA)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

