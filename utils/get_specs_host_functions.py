import requests
import re
import json

# URL of the polkadot host-api specification
URL = "https://raw.githubusercontent.com/w3f/polkadot-spec/main/docs/chap-host-api.md"
SPECS_HOST_API_NAME = "scripts/host_api/specs_host_api.json"

response = requests.get(URL)

def parse_types(segment):
    # segment is of type: 
    # (param $root i32) (param $proof i64)
    # (param $key i64) (param $value i64)
    # we need to remove param and $key
    cleaned_segment = re.sub(r'\bparam\b|\$\w+', '', segment)
    types = re.findall(r'\b[a-zA-Z0-9_]+\b', cleaned_segment)

    return types

def parse_result_types(segment):
    # Remove the 'result' keyword from the segment, then parse the types
    cleaned_segment = re.sub(r'\bresult\b', '', segment)
    types = re.findall(r'\b[a-zA-Z0-9_]+\b', cleaned_segment)
    return types


if response.status_code == 200:
    markdown_text = response.text

    # The main pattern matches each function definition, 
    # capturing the entire parameters and results segments
    pattern = re.compile(r'\(func \$(\w+)((?:(?:\s|\n)*\(param[^\)]*\))*)((?:(?:\s|\n)*\(result[^\)]*\))*)', re.MULTILINE | re.DOTALL)
    
    functions = []
    for match in pattern.finditer(markdown_text):
        func_name = match.group(1)

        # Extract parameters and results
        params_segment = match.group(2)
        results_segment = match.group(3)

        params = []
        if params_segment:
            params = parse_types(params_segment)

        results = []
        if results_segment:
            results = parse_result_types(results_segment)

        function = {
            "name": func_name,
            "params": params,
            "results": results
        }

        functions.append(function)

    # Save function information to a JSON file
    with open(SPECS_HOST_API_NAME, "w") as file:
        json.dump(functions, file, indent=4)

    print(f"{len(functions)} host-api function specifications saved to {SPECS_HOST_API_NAME}")
else:
    print("Failed to retrieve the markdown file")

