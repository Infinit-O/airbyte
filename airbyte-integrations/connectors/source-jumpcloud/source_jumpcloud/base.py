from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import arrow
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams import IncrementalMixin

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

class JumpcloudV2Stream(HttpStream, ABC):
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

    Notes specific to Jumpcloud V2 API:
    * Some of the V2 API endpoints do not support "skip" or "limit". It's not consistent across all endpoints
    """

    url_base = "https://console.jumpcloud.com/api/v2/"

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config
        self.limit = 100
        self.offset = 0
        self.keep_going = True

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
        if self.keep_going:
            self.offset += self.limit
            return {"skip": self.offset}
        else:
            return None

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
            return {"skip": next_page_token.get("skip"), "limit": self.limit}
        else:
            return {"limit": self.limit}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.

        :return an iterable containing each record in the response
        """
        contents = response.json()
        if not contents:
            self.keep_going = False
            return None
        else:
            yield from contents
        
# Basic incremental stream
class JumpcloudV2IncrementalStream(JumpcloudV2Stream, IncrementalMixin):
    state_checkpoint_interval = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # NOTE: The SystemInsights endpoints are the only ones that support a limit of 1000.
        self.limit = 1000

        self._state = {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "collection_time"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        if current_stream_state == {}:
            self.state = latest_record[self.cursor_field]
            return {self.cursor_field: latest_record['collection_time']}
        else:
            records = {}
            records[current_stream_state[self.cursor_field]] = arrow.get(current_stream_state[self.cursor_field])
            records[latest_record[self.cursor_field]] = arrow.get(latest_record[self.cursor_field])
            latest_record = max(records.items(), key=lambda x: x[1])
            self.state = latest_record[0]
            return {self.cursor_field: latest_record[0]}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        def __newer_than_latest(recorded_state: arrow.Arrow, latest_record: dict) -> bool:
            latest_record_date = arrow.get(latest_record[self.cursor_field])
            if recorded_state > latest_record_date:
                return False
            else:
                return True

        contents = response.json()
        if not contents:
            self.keep_going = False
            return None
        else:
            # NOTE: Stream contents appear to be in order already, so this _might_ be redundant.
            #       but better safe than sorry...
            sorted_contents = sorted(contents, key=lambda x: arrow.get(x["collection_time"]))
            if stream_state:
                stored_date = arrow.get(stream_state[self.cursor_field])
                if __newer_than_latest(stored_date, sorted_contents[-1]) is False:
                    self.keep_going = False
                    return None
                else:
                    only_the_newest = [x for x in sorted_contents if __newer_than_latest(stored_date, x)]
                    yield from only_the_newest
            else:
                # NOTE: no reversal needed as its already in ascending order (at least it looks like that)
                yield from sorted_contents
