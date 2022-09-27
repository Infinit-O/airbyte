# NOTE: This is a utility script - 
# TO interact with the Netsuite API over Postman you need
# to sign a JWT with the public key half of the keypair that's
# been uploaded to Netsuite's config, then include that
# JWT in a POST request to Netsuite's OAUTH endpoint.
import json

import jwt
import pendulum

with open("secrets/config.json", "r") as F:
    secrets = json.loads(F.read())

with open("secrets/private_key.pem", "r") as F:
    private_key = F.read()

iat = int(pendulum.now().timestamp())
exp = int(iat + 3600)

headers = {
    "kid": secrets["certificate_id"] 
}

payload = {
    "iss": secrets["client_id"],
    "scope": "rest_webservices",
    "aud": f"https://{secrets['account_id']}.suitetalk.api.netsuite.com/services/rest/record/v1",
    "iat": iat,
    "exp": exp
}

encoded = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)

print(encoded)
