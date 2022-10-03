
from abc import ABC, abstractmethod
from re import S
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode

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

    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config

    @property
    def url_base(self):
        account_id = self.config["account_id"]
        return f"https://{account_id}.suitetalk.api.netsuite.com/services/rest/record/v1/"

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
        data: dict = response.json()
        has_more: bool = data["hasMore"]

        if has_more:
            return {"next_page": "".join([x["href"] for x in data["links"] if x["rel"] == "next"])}

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
        data: dict = response.json()
        yield from data["items"]

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        if next_page_token:
            return next_page_token["next_page"]


class NetsuiteChildStream(NetsuiteStream):
    @property
    @abstractmethod
    def parent(self):
        pass

    @property
    @abstractmethod
    def fk_name(self):
        pass

    @property
    @abstractmethod
    def fk(self):
        pass

    @property
    @abstractmethod
    def path_template(self):
        pass
    
    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        fkid = stream_slice[self.fk_name]
        return self.path_template.format(entity_id=fkid)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        data: dict = response.json()
        yield from [data]

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # find the auth!
        if self._session.auth:
            auth = self._session.auth
        elif self._authenticator:
            auth = self._authenticator

        parent = self.parent(authenticator=auth, config=self.config)
        parent_stream_slices = parent.stream_slices(
            sync_mode=SyncMode.full_refresh,
            cursor_field=cursor_field,
            stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = parent.read_records(
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
                stream_slice=stream_slice,
                stream_state=stream_state
            )

            # iterate over all parent records with current stream_slice
            for record in parent_records:
                yield {self.fk_name: record[self.fk]}
