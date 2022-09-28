from base64 import b64encode

if __name__ == "__main__":
    with open("secrets/private_key.pem", "rb") as F:
        key_contents = F.read()

    encoded: bytes = b64encode(key_contents)
    str_encoded = encoded.decode("utf-8")

    print(str_encoded)
