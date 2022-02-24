#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, MutableMapping, Tuple, Iterable, Optional

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .base import ZohoDeskStream

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

class Organizations(ZohoDeskStream):
    """ 
        Important Note: this stream fetches all organizations that the current user belongs to.
        This means that whatever service account is used in production needs to belong to whatever
        organizations you need information on. 
    """
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "organizations"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.

        Important note: despite being listed as the general pagination method for the entire API
        certain endpoints do NOT honor the "limit" param and will 422 if it is received.

        This endpoint is one such endpoint, hence request_params is overridden here.
        """
        return {}

class Agents(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "agents"

class Profiles(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "profiles"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.

        Important note: despite being listed as the general pagination method for the entire API
        certain endpoints do NOT honor the "limit" param and will 422 if it is received.

        This endpoint is one such endpoint, hence request_params is overridden here.
        """
        return {}

class Roles(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "roles"

class Teams(ZohoDeskStream):
    """ 
        Important Note: this stream fetches all teams that the current user belongs to.
        This means that whatever service account is used in production needs to belong to whatever
        teams you need information on. 
    """
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "teams"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.

        Important note: despite being listed as the general pagination method for the entire API
        certain endpoints do NOT honor the "limit" param and will 422 if it is received.

        This endpoint is one such endpoint, hence request_params is overridden here.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.

        WHY DID THEY DO THIS WHY WHY WHY

        :return an iterable containing each record in the response
        """
        yield from response.json().get("teams")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        THE TEAMS ENDPOINT IS DUMB

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        data: List[dict] = response.json().get("teams")
        # NOTE: if there are less than self.limit records in the response there are no other pages.
        if len(data) < self.limit:
            return None
        else:
            self.start_from += self.limit
            return {"from": self.start_from}

class Departments(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "departments"

# Source
class SourceZohoDesk(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        oauth_id: str = config["client_id"]
        oauth_secret: str = config["client_secret"]
        oauth_refresh_token: str = config["refresh_token"]
        oauth_refresh_token_endpoint: str = config["token_refresh_endpoint"]
        oauth_scopes: List[str] = config["oauth_scopes"]
        if oauth_id == "":
            return False, "oAuth ID cannot be an empty string."
        if oauth_secret == "":
            return False, "oAuth secret cannot be an empty string."
        if oauth_refresh_token == "":
            return False, "oAuth refresh token cannot be an empty string."
        if oauth_refresh_token_endpoint == config["token_refresh_endpoint"] == "":
            return False, "oAuth refresh token endpoint cannot be an empty string."
        if oauth_scopes == []:
            return False, "oAuth scopes cannot be empty."

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        auth = Oauth2Authenticator(
            token_refresh_endpoint=config["token_refresh_endpoint"],
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
            scopes=config["oauth_scopes"]
        )
        return [
            Organizations(authenticator=auth),
            Agents(authenticator=auth),
            Profiles(authenticator=auth),
            Roles(authenticator=auth),
            Teams(authenticator=auth),
            Departments(authenticator=auth),
        ]
