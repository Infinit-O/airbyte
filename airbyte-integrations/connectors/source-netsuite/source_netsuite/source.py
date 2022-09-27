#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from base64 import urlsafe_b64decode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import jwt
import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth.abstract_oauth import AbstractOauth2Authenticator

class NetsuiteOauth2Authenticator(AbstractOauth2Authenticator):
    # NOTE: Netsuite's OAuth2 implementation for server-to-server
    #       communication calls for a public/private keypair and
    #       has the following attributes:
    #       - there is no refresh token, nor any way to refresh an access token
    #       - on first issue the server must provide a 'client assertion'
    #       that is a JWT bearing certain properties and signed by the
    #       private half of the keypair.
    #       - the access token thus granted lasts only one hour.
    #       - "refreshing" thus is just getting a new token
    def __init__(self, client_id: str, certificate_id: str, private_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client_id = client_id
        self.certificate_id = certificate_id
        self.private_key = private_key

    def __decode_private_key(self) -> str:
        bytes_private_key = bytes(self.private_key, "utf-8")
        decoded_key = urlsafe_b64decode(bytes_private_key)
        return str(decoded_key) 

    def __generate_signed_jwt(self) -> str:
        headers = {
            "kid": self.certificate_id
        }

        iat = int(pendulum.now().timestamp())
        exp = int(iat + 3600)
        payload = {
            "iss": self.client_id,
            "scope": "rest_webservices",
            "aud": f"https://{self.account_id}.suitetalk.api.netsuite.com/services/rest/record/v1",
            "iat": iat,
            "exp": exp
        }

        decoded_private_key: str = self.__decode_private_key()
        encoded = jwt.encode(payload, decoded_private_key, algorithm="RS256", headers=headers)

        return encoded

    def get_refresh_token(self) -> str:
        pass

# Basic full refresh stream
class NetsuiteStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class NetsuiteStream(HttpStream, ABC)` which is the current class
    `class Customers(NetsuiteStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(NetsuiteStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalNetsuiteStream((NetsuiteStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    def url_base(self):
        account_id = self.config["account_id"]
        return f"https://{account_id}.suite_talk.api.netsuite.com/services/rest/record/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield {}


class Customers(NetsuiteStream):
    primary_key = "customer_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "customers"

# Source
class SourceNetsuite(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        cant_be_empty = ["account_id", "client_id", "certificate_id"]
        for x in cant_be_empty:
            if config[x] == "":
                return False, f"{x} cannot be empty string!"

        # check if the key can be decoded
        key = config["private_key"]
        bytes_key = bytes(key, "utf-8")
        raw_private_key = str(urlsafe_b64decode(bytes_key))
        if not ("BEGIN PRIVATE KEY" in raw_private_key) or not ("END PRIVATE KEY" in raw_private_key):
            return False, "Private key can't be decoded! Check that it was correctly encoded in Base64."

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = NetsuiteOauth2Authenticator(
            config["client_id"],
            config["certificate_id"],
            config["private_key"]
        )
        return []
