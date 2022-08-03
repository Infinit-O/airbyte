from typing import Optional, Mapping, Any, MutableMapping, Iterable, List
from abc import ABC, abstractmethod

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode

class WorkplaceByMetaStream(HttpStream, ABC):
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
    `class WorkplaceByMetaStream(HttpStream, ABC)` which is the current class
    `class Customers(WorkplaceByMetaStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(WorkplaceByMetaStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalWorkplaceByMetaStream((WorkplaceByMetaStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://graph.facebook.com/"

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
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if self.fields:
            return {"fields": ",".join(self.fields)}
        else:
            return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        # import pdb
        # pdb.set_trace()
        data = response.json()
        yield from data["data"]

class WorkplaceByMetaSubstream(WorkplaceByMetaStream):
    @property
    @abstractmethod
    def path_template(self):
        pass

    @property
    @abstractmethod
    def parent_stream(self):
        pass

    # NOTE: This should always be "id" in this case, but just in case...
    @property
    @abstractmethod
    def foreign_key(self):
        pass
    
    def stream_slices(self,
        *,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        active_parent = self.parent_stream(authenticator=self._session.auth)
        for item in active_parent.read_records(SyncMode.full_refresh):
            yield {self.foreign_key: item[self.foreign_key]}

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        streamslice = {} or stream_slice
        return self.path_template.format(entity_id=streamslice[self.foreign_key])
