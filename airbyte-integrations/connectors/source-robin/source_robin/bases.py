from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode

from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class RobinStream(HttpStream, ABC):
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
    `class RobinStream(HttpStream, ABC)` which is the current class
    `class Customers(RobinStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(RobinStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalRobinStream((RobinStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://api.robinpowered.com/v1.0/"

    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config

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
        try:
            paging = response.json()["paging"]
        except KeyError:
            return None

        if paging["has_next_page"] is True:
            return {
                "current_page": paging["page"],
                "next_page": int(paging["page"]) + 1
            }
        else:
            return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return {
                "page": next_page_token["next_page"]
            }
        else:
            return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        resp = response.json()
        yield from resp["data"]


class RobinChildStream(RobinStream):
    @property
    @abstractmethod
    def parent_stream(self):
        pass

    @property
    @abstractmethod
    def path_template(self):
        pass

    @property
    @abstractmethod
    def foreign_key(self):
        pass

    @property
    @abstractmethod
    def foreign_key_name(self):
        pass

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(authenticator=self._authenticator, config=self.config)
        for x in ps.read_records(SyncMode.full_refresh):
            yield {self.foreign_key_name: x[self.foreign_key]}
