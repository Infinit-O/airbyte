from abc import ABC, abstractmethod
from typing import Optional, Mapping, Any, Iterable, MutableMapping

import requests
from airbyte_cdk.sources.streams.http import HttpStream

# Basic full refresh stream
class ZohoRecruitStream(HttpStream, ABC):
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
    `class ZohoRecruitStream(HttpStream, ABC)` which is the current class
    `class Customers(ZohoRecruitStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ZohoRecruitStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalZohoRecruitStream((ZohoRecruitStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://recruit.zoho.com/recruit/v2/"

    @property
    @abstractmethod
    def envelope_name(self):
        pass

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
        :return an iterable containisng each record in the response
        """
        # NOTE: Workaround for the fact that Zoho APIs seem to return 204 no content
        #       in place of an empty JSON response. sigh.
        if response.status_code == 204:
            yield from []
        else:
            yield from response.json().get(self.envelope_name, [])
