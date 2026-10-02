import json

def encode(message):
    return (json.dumps(message, separators=(",", ":")) + "\n").encode()

def decode(line):
    return json.loads(line.decode())
