from abc import ABC
from typing import Mapping, Any, Optional, Iterable, MutableMapping, List

import requests
from airbyte_cdk.sources.streams.http import HttpStream

class ZohoDeskStream(HttpStream, ABC):
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
    `class ZohoDeskStream(HttpStream, ABC)` which is the current class
    `class Customers(ZohoDeskStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ZohoDeskStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalZohoDeskStream((ZohoDeskStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://desk.zoho.com/api/v1/"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # NOTE: Pagination options here. Limit should be no greater than 50
        #       start_from is the offset, and defaults to 1.
        # NOTE: Some endpoints do not honor limit / start_from. Streams for said
        #       endpoints will selectively override request_params() whenever that
        #       is the case.
        self.limit = 10 
        self.start_from = 1  

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
        data: List[dict] = response.json().get("data")
        # NOTE: if there are less than self.limit records in the response there are no other pages.
        if len(data) < self.limit:
            return None
        # NOTE: I'm sorry if this doesn't make any sense. Please see the entry for `channels` in
        #       WTF.md for more information 
        if len(data) > self.limit:
            return None
        else:
            # NOTE: -1 because certain endpoints will fail when limit happens to be 1 over.
            # NOTE: Zoho desk pagination is weird.
            self.start_from += self.limit - 1
            return {"from": self.start_from}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return {"limit": self.limit, "from": next_page_token["from"]}
        else:
            return {"limit": self.limit}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield from response.json().get("data")
