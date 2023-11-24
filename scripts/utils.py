import json

from scalecodec.types import Vec, ScaleBytes, String, ScaleType
from scalecodec.base import RuntimeConfiguration

RPC_METHOD = "zondax_host_api" 

class RpcMessage:
    def __init__(self, method, params):
        self.method = method
        self.params = params
    
    def to_dict(self):
        return {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.params,
            "id": 1
        }

async def send_messages(websocket, messages):
    responses = []  # Initialize an empty list to collect responses
    
    # lets support the case we sent only one message 
    if not isinstance(messages, list):
        messages = [messages]

    for message in messages:
        await websocket.send(message)
        print(f"> Sent: {message}")

        response = await websocket.recv()
        print(f"< Received: {response}")
        responses.append(response)

    # Return either a single response or a list of responses
    return responses if len(responses) > 1 else responses[0]


def host_api_msg(method,args):
    args = [method, args]
    message = RpcMessage(RPC_METHOD, args)
    return json.dumps(message.to_dict()) 

# TODO: Add support for other types 
# this work only for BYtes
def scale_encode(data, data_type="Bytes"):
    encoded_data = []
    for item in data:
        scale_obj = RuntimeConfiguration().create_scale_object('Bytes')
        encoded_data += list(scale_obj.encode(item).data)

    return encoded_data

# TODO: Add support for more types
def scale_decode(encoded_data, data_type):
    byte_data = bytes(encoded_data)
    scale_bytes = ScaleBytes(byte_data)
    scale_obj = RuntimeConfiguration().create_scale_object(data_type, scale_bytes)
    decoded_value = scale_obj.decode()

    return decoded_value
