
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
    
