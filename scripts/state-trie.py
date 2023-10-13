import asyncio
import websockets
import json

import utils


with open('./scripts/hex_long.json') as f:
    hex_long = json.load(f)

def make_payload(method, value):
    message = utils.RpcMessage(method, {"input": value})
    return json.dumps(message.to_dict())

def prepare_testing_data():
    test_data = [
        (make_payload("zondax_trieRoot", {"01": "01"})),
        (make_payload("zondax_insertAndDelete", {"01": "01"})),
        (make_payload("zondax_trieRoot", {"02": "02", "03": "03"}))
    ]
    return test_data

async def main():
    uri = "ws://127.0.0.1:9944"
    async with websockets.connect(uri) as websocket:

        test_data = prepare_testing_data()
        messages = [message for message in test_data]
        responses = await utils.send_messages(websocket, messages)  # collect the responses

        for (message), response in zip(test_data, responses):
            # Parse the response
            response_data = json.loads(response)
            result = response_data.get('result', '')  # Adjust this line based on the actual response format

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())