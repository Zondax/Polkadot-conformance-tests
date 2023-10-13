import requests
import re
import json

# URL of the polkadot host-api specification
URL = "https://raw.githubusercontent.com/w3f/polkadot-spec/main/docs/chap-host-api.md"
SPECS_HOST_API_NAME = "scripts/host_api/specs_host_api.json"

response = requests.get(URL)

if response.status_code == 200:
    markdown_text = response.text
    
    # use regex to get function names described in the specification.
    pattern = re.compile(r'\(func \$(\w+)')
    
    function_names = pattern.findall(markdown_text)
    
    # Save function names to a JSON file
    with open(SPECS_HOST_API_NAME, "w") as file:
        json.dump(function_names, file, indent=4)
    
    print(f"{len(function_names)}  host-api function names saved to " + SPECS_HOST_API_NAME)
else:
    print("Failed to retrieve the markdown file")
