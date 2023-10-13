import asyncio
import websockets
import json

import utils

# for a u32: 42 and according to the scale encoding docs,
# the encoded data should be:
EXPECTED_RESPONSE_U32 = '2a000000'
EXPECTED_RESPONSE_VEC = '1804080f10172a'
EXPECTED_RESPONSE_STR = '185a6f6e646178'
EXPECTED_RESPONSE_I64 = 'ffffffff'
EXPECTED_RESPONSE_F64 = '0000000000004540'
EXPECTED_RESPONSE_TUPLE = '0100185a6f6e646178'

# for more info go: https://docs.substrate.io/reference/scale-codec/

def make_payload(variant_name, value):
    message = utils.RpcMessage("scale_encode", {"test" : {variant_name: value}})
    return json.dumps(message.to_dict())


# pub enum ScaleMsg {
# 	U32(u32),
# 	I64(i32),
# 	F64(f64),
# 	Str(String),
# 	Vec(Vec<u8>),
# 	Tuple((u16, String)),
# }

def prepare_testing_data():
    test_data = [
        (make_payload("U32", 42), EXPECTED_RESPONSE_U32),
        (make_payload("Str", "Zondax"), EXPECTED_RESPONSE_STR),
        (make_payload("I64", -1), EXPECTED_RESPONSE_I64),
        (make_payload("Vec", [4, 8, 15, 16, 23, 42]), EXPECTED_RESPONSE_VEC),
        (make_payload("F64", 42.0), EXPECTED_RESPONSE_F64),
        (make_payload("Tuple", (1, "Zondax")), EXPECTED_RESPONSE_TUPLE)
    ]
    return test_data

async def main():
    uri = "ws://127.0.0.1:9944"
    async with websockets.connect(uri) as websocket:

        test_data = prepare_testing_data()
        messages = [message for message, _ in test_data]
        responses = await utils.send_messages(websocket, messages)  # collect the responses

        for (message, expected_response), response in zip(test_data, responses):
            # Parse the response
            response_data = json.loads(response)
            result = response_data.get('result', '')  # Adjust this line based on the actual response format

            # Compare the result with the expected response
            assert result == expected_response, f"Unexpected result: {result} for message: {message}"

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())


