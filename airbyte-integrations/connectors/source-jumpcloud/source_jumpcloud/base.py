from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources.streams.http import HttpStream

# Basic full refresh stream
class JumpcloudStream(HttpStream, ABC):
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
    `class JumpcloudStream(HttpStream, ABC)` which is the current class
    `class Customers(JumpcloudStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(JumpcloudStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalJumpcloudStream((JumpcloudStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://console.jumpcloud.com/api/"

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config
        self.offset = 0
        self.limit = 100
        self.total = 0

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
        # import pdb
        # pdb.set_trace()
        if self.offset < self.total:
            self.offset = self.offset + self.limit
            return {'skip': self.offset}
        else:
            return {} 

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        # NOTE: Auth headers injected here because the included TokenAuthenticator won't do
        #       {'x-api-token': 'token'} correctly. Specifying "" for auth_method will still
        #       cause a blank space to be included the token string, which causes an error
        #       when requests tries to send one out.
        # NOTE: This is because TokenAuthenticator constructs the header value by format-string
        #       substitution: `return f"{auth_method} {auth_value}"` and a blank auth_method
        #       will still cause a space to be inserted in front of auth_value, rendering it invalid.
        # NOTE: Do _NOT_ pass an authenticator in until I can find a way around this.
        return {'x-api-key': self.config['api_key']}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.

        :return a dictionary
        """
        if next_page_token:
            return {'skip': next_page_token.get('skip'), 'limit': self.limit}
        else:
            return {'limit': self.limit}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.

        :return an iterable containing each record in the response
        """
        self.total = int(response.json().get("totalCount"))
        yield from response.json().get("results")