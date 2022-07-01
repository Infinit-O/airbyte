from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union, List

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

class DesktopCentralStream(HttpStream, ABC):
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
    `class DesktopCentralStream(HttpStream, ABC)` which is the current class
    `class Customers(DesktopCentralStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(DesktopCentralStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalDesktopCentralStream((DesktopCentralStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """
    @property
    def envelope_name(self):
        return ""

    @property
    def url_base(self):
        return self.config["base_url"]

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.stop_paginating = False
        self.universal_page_limit = 100
        self.current_page = 1
        self.last_page = -1

    @property
    def max_retries(self) -> Union[int, None]:
        """
        Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        return 100

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return 160

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
        envelope = response.json()["message_response"]

        if self.stop_paginating:
            return None

        keys = ["total", "limit", "page"] 
        checks = [key in envelope.keys() for key in keys]

        if all(checks):
            # NOTE: if total is less page limit, there is only 1 page of information (1/2)
            if int(envelope["total"]) < int(self.universal_page_limit):
                return None
            else:
                # NOTE: (2/2) otherwise we return a token containing pagination details.
                # NOTE: The exact "last page" needs to be calculated to make sure we don't
                #       accidentally "circle around" and scrape the first page again by accident.
                if self.last_page < 0:
                    self.last_page = int(envelope["total"] / self.universal_page_limit) + 1
                return {
                    "total": envelope["total"],
                    "limit": self.universal_page_limit,
                    "page": envelope["page"]
                }
        else:
            return None

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        Override to return a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..
        """

        # NOTE: SSL Cert Verification disabled because the source has a self-signed certificate
        return {}
        # return {"verify": False}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            current = int(next_page_token["page"])
            # NOTE: are we on the last page?
            if self.last_page < current:
                self.stop_paginating = True
            # NOTE: get the next page 
            return {"page": current + 1, "pagelimit": self.universal_page_limit}
        else:
            return {"pagelimit": self.universal_page_limit}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        # import pdb
        # pdb.set_trace()
        data = response.json()
        items = data["message_response"][self.envelope_name]
        for item in items:
            item["url"] = response.request.url
        yield from items 

class DesktopCentralSubstream(DesktopCentralStream):
    @property
    @abstractmethod
    def path_template(self):
        pass

    @property
    @abstractmethod
    def parent_stream(self):
        pass

    def stream_slices(self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        items = self.parent_stream(authenticator=self._authenticator, config=self.config)
        for item in items.read_records(sync_mode=SyncMode.full_refresh):
            yield {self.foreign_key: item[self.foreign_key]}

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        streamslice = stream_slice or {}
        return self.path_template.format(entity_id=streamslice[self.foreign_key])

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        if self.stop_paginating:
            yield from []
        data = response.json()
        items = data["message_response"][self.envelope_name]
        # NOTE: I think this might be faster on average than doing a list comprehension
        #       to update the items because it will yield BEFORE doing the next one
        #       i.e it updates then yields one-at-a-time.
        for item in items:
            item[self.foreign_key] = kwargs["stream_slice"][self.foreign_key]
            yield item
