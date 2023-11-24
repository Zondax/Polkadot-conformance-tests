import asyncio
import websockets
import json

import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

CRYPTO_GENERATE = "ZondaxTest_sr25519_generate"
CRYPTO_SIGN = "ZondaxTest_sr25519_sign"
CRYPTO_VERIFY = "ZondaxTest_sr25519_verify"
CRYPTO_MSG = "zondax_message"

# MUST be 4 bytes
KEY_TYPE_ID = "zndx"


URI = "ws://127.0.0.1:9944"

async def sr25519_key(websocket, key_id, seed = []):
    # key_id + Option<Seed>, which we set as None.
    args = utils.scale_encode([KEY_TYPE_ID.encode('utf8'), []], 'Vec<Bytes>')

    # we remove the length of the key_id. for some reason 
    # the rust scale decoder for the runtime does not expect that 
    # in the args bytes. The reason might be that the function takes in 
    # an [u8; 4] so no reason to add 4, just scale encode and that is it all.
    msg = utils.host_api_msg(CRYPTO_GENERATE, args[1:])

    response = await utils.send_messages(websocket, msg)
    response_data = json.loads(response)

    pub_key = response_data.get('result', '')

    return pub_key

async def sr25519_sign(websocket, key_id, pub_key, msg):
    # message must be encoded and length prefixed
    encoded_message = utils.scale_encode([msg.encode('utf8')])

    args = [key_id.encode('utf8'), pub_key, encoded_message]
    flattened_args = [item for sublist in args for item in sublist]
    args = list(flattened_args)

    msg = utils.host_api_msg(CRYPTO_SIGN, args)
    response = await utils.send_messages(websocket, msg)
    response_data = json.loads(response)

    signature = response_data.get('result', '')

    # V and Signature
    return (signature[0], signature[1:])


async def sr25519_verify(websocket, signature, msg, pub_key):
    encoded_message = utils.scale_encode([msg.encode('utf8')])
    args = [signature, encoded_message, pub_key]
    args = list( [item for sublist in args for item in sublist] )

    msg = utils.host_api_msg(CRYPTO_VERIFY, args)

    response = await utils.send_messages(websocket, msg)
    response_data = json.loads(response)

    valid = response_data.get('result', '')

    # 1 true in case signature is valid
    return len(valid) == 1 and valid[0] == 1


async def check_sr25519(websocket):

    pub_key = await sr25519_key(websocket, KEY_TYPE_ID)

    (v, signature) = await sr25519_sign(websocket, KEY_TYPE_ID, pub_key, CRYPTO_MSG)

    valid = await sr25519_verify(websocket, signature, CRYPTO_MSG, pub_key)

    assert valid == True, f"Invalid signature!"

async def main():
    async with websockets.connect(URI) as websocket:
        await check_sr25519(websocket)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

