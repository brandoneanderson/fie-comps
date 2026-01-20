import json

def readfile(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    print(json.dumps(data, indent=4))