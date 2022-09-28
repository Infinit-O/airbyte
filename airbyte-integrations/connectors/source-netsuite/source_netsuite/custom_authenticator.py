from base64 import b64decode

from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
import jwt
import pendulum
import requests

class B64Utility():
    def __init__(self, encoded_content: str):
        self.encoded_content: str = encoded_content 

    def decode_content(self):
        bytestream: bytes = bytes(self.encoded_content, "utf-8")
        decoded_raw: bytes = b64decode(bytestream)
        str_decoded_raw: str = decoded_raw.decode("utf-8")
        return str_decoded_raw

class NetsuiteOauth2Authenticator(Oauth2Authenticator):
    # NOTE: Netsuite's OAuth2 implementation for server-to-server
    #       communication calls for a public/private keypair and
    #       has the following attributes:
    #       - there is no refresh token, nor any way to refresh an access token
    #       - on first issue the server must provide a 'client assertion'
    #       that is a JWT bearing certain properties and signed by the
    #       private half of the keypair.
    #       - the access token thus granted lasts only one hour.
    #       - "refreshing" thus is just getting a new token
    def __init__(self,
        client_id: str,
        certificate_id: str,
        private_key: str,
        account_id: str,
        *args,
        **kwargs
    ):

        self.client_id: str = client_id
        self.certificate_id: str = certificate_id

        self.decoder = B64Utility(private_key)

        current_time = pendulum.now()
        expiry_time = current_time.add(hours=1)
        self.iat: int = int(current_time.timestamp())
        self.exp: int = int(expiry_time.timestamp())
        # NOTE: The intent here is to force the get_access_token() method
        #       to go and fetch+set a new token on init. By the time
        #       it reaches this line now() != current_time at least I
        #       hope it isn't
        self.set_token_expiry_date(current_time)

        self.account_id: str = account_id
        self._token_refresh_endpoint: str = "https://{account_id}.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token"
        self.get_access_token()

    def __generate_signed_jwt(self) -> str:
        headers: dict = {
            "kid": self.certificate_id
        }

        payload: dict = {
            "iss": self.client_id,
            "scope": "rest_webservices",
            "aud": f"https://{self.account_id}.suitetalk.api.netsuite.com/services/rest/record/v1",
            "iat": self.iat,
            "exp": self.exp
        }

        decoded_private_key: str = self.decoder.decode_content()

        encoded: str = jwt.encode(
            payload,
            decoded_private_key,
            algorithm="RS256",
            headers=headers
        )

        return encoded

    def refresh_access_token(self) -> str:
        jwt = self.__generate_signed_jwt()
        try:
            response = requests.post(
                url=self.get_token_refresh_endpoint(),
                data={
                    "grant_type": "client_credentials",
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": jwt
                }
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], int(response_json["expires_in"])
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

    def get_token_refresh_endpoint(self) -> str:
        return self._token_refresh_endpoint.format(account_id=self.account_id)
