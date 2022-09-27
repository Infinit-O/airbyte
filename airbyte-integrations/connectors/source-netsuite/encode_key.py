from base64 import urlsafe_b64encode, urlsafe_b64decode
from platform import java_ver


if __name__ == "__main__":
    with open("secrets/private_key.pem", "rb") as F:
        key_contents = F.read()

    encoded = urlsafe_b64encode(key_contents)
    print(str(encoded, 'utf-8'))
