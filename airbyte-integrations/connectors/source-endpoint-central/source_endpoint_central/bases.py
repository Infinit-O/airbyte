from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union, List
from time import sleep

import requests
from http import HTTPStatus
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

EMPTY_BODY_STATUSES = (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)

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
    # NOTE: Very temporary workaround for the infrastructure troubles we're having on the devops side
    # Please don't change this without alerting me first. 
    @property
    def verify_ssl(self):
        return False

    @property
    def envelope_name(self):
        return ""

    @property
    def pacing(self) -> float:
        """ 
        Returns the number of seconds to wait before sending a request. Used for pacing requests to strict APIs. It can
        be a floating point value for precision, and will be passed to sleep() when called.
        """
        return 1.75

    @property
    def url_base(self):
        return self.config["base_url"]
    
    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        verify = self.verify_ssl
        return {
            'verify': verify
        }

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
        try:
            envelope = response.json()["message_response"]
        except KeyError:
            return None

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
        data = response.json()

        items = data["message_response"][self.envelope_name]

        for item in items:
            item["url"] = response.request.url
        yield from items

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        self.logger.debug("kwargs: {}".format(request_kwargs))
        sleep(self.pacing)
        resp = super()._send(request, request_kwargs)
        return resp

class SummaryOverride(DesktopCentralStream):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        data = response.json()
        summary = data["message_response"][self.envelope_name]
        summary["url"] = response.request.url
        yield from [summary]

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

        # NOTE: In the computer_summary stream, computers that don't have the DesktopCentral
        #       agent installed will instead have a row that contains an error message, without
        #       "message_response" in it. This try/except block is meant to get around that (1/2)
        try:
            items = data["message_response"][self.envelope_name]
        except KeyError:
            items = data

        # NOTE: (2/2) the computer_summary stream also returns a single dictionary as opposed to
        #       a LIST of dictionaries, so we handle that here.
        if isinstance(items, dict):
            items[self.foreign_key] = kwargs["stream_slice"][self.foreign_key]
            items["url"] = response.request.url
            yield from [items]
        else:
            # NOTE: I think this might be faster on average than doing a list comprehension
            #       to update the items because it will yield BEFORE doing the next one
            #       i.e it updates then yields one-at-a-time.
            for item in items:
                item[self.foreign_key] = kwargs["stream_slice"][self.foreign_key]
                item["url"] = response.request.url
                yield item

class DesktopCentralThreatStream(HttpStream, ABC):
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
    # NOTE: Very temporary workaround for the infrastructure troubles we're having on the devops side
    # Please don't change this without alerting me first. 
    @property
    def verify_ssl(self):
        return False

    @property
    def envelope_name(self):
        return ""

    @property
    def pacing(self) -> float:
        """ 
        Returns the number of seconds to wait before sending a request. Used for pacing requests to strict APIs. It can
        be a floating point value for precision, and will be passed to sleep() when called.
        """
        return 1.75

    @property
    def url_base(self):
        return self.config["base_url"]
    
    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        verify = self.verify_ssl
        return {
            'verify': verify
        }

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
        try:
            envelope = response.json()["metadata"]
        except KeyError:
            return None

        if self.stop_paginating:
            return None

        keys = ["totalRecords", "pageLimit", "page"] 
        checks = [key in envelope.keys() for key in keys]
        self.totalRecords=envelope["totalRecords"]
        self.page=envelope["page"]
        self.logger.info(f"Total Records: {self.totalRecords}")

        if all(checks):
            # NOTE: if total is less page limit, there is only 1 page of information (1/2)
            if int(envelope["totalRecords"]) < int(self.universal_page_limit):
                return None
            else:
                # NOTE: (2/2) otherwise we return a token containing pagination details.
                # NOTE: The exact "last page" needs to be calculated to make sure we don't
                #       accidentally "circle around" and scrape the first page again by accident.
                if self.last_page < 0:
                    self.last_page = int(int(envelope["totalRecords"]) / self.universal_page_limit) + 1
                    
                return {
                    "totalRecords": envelope["totalRecords"],
                    "pageLimit": self.universal_page_limit,
                    "page": envelope["page"]
                }
        else:
            return None


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
            return {"page": current + 1, "pageLimit": self.universal_page_limit}
        else:
            return {"pageLimit": self.universal_page_limit}
        
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """

        data = response.json()
        try:
            items = data["message_response"][self.envelope_name]
            for item in items:
                item["url"] = response.request.url
            yield from items
        except KeyError:
            items = data
            
    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        self.logger.debug("kwargs: {}".format(request_kwargs))
        sleep(self.pacing)
        resp = super()._send(request, request_kwargs)
        return resp
