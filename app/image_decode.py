import base64


def decode(data):
    return base64.b64decode(f"{data}")
