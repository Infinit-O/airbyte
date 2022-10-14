# NETSUITE SPECIFIC NOTES
Netsuite has two OAuth flows for integrations, one designed for apps that require user interaction, and one suitable for server-to-server applications. IOM's Airbyte connector uses the latter.

## HOW IT WORKS

1. Register new app with Netsuite. Take note of client_id, it is important and will only be displayed once.
1. Generate a public / private key pair (follow the instructions in their docs)
1. Upload the public half to Netsuite, and take note of the certificate ID.
1. Take the private key and encode its contents with base64.
1. Place the b64-encoded private key, the certificate id, the client id, and the company's account number in a config.json file under the `secrets` subdirectory.
1. Using `sign_jwt.py` in this project's subdirectory, generate a JWT.
1. Pass the JWT from the previous step to the Netsuite Oauth endpoint, and if all is right you will get an access token valid for one hour.
1. When you need to refresh, repeat previous 2 steps to get a new access token.

## IMPORTANT NOTES
Authorization is done via bearer token, in the usual OAuth way.
