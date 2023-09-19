from abc import ABC
from re import I
from typing import Mapping, Any, Optional, Iterable, MutableMapping, List, Union

import requests
import arrow
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode

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
    
    # def backoff_time(self, response: requests.Response):
    #     return 160 
    @property
    def max_retries(self) -> Union[int, None]:
        return 50 

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

class ZohoDeskIncrementalStream(ZohoDeskStream):
    @property
    def cursor_field(self):
        return "createdTime"

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        if current_stream_state == {}:
            return {self.cursor_field: latest_record[self.cursor_field]}
        else:
            records = {}
            records[current_stream_state[self.cursor_field]] = arrow.get(current_stream_state[self.cursor_field])
            records[latest_record[self.cursor_field]] = arrow.get(latest_record[self.cursor_field])
            latest_record = max(records.items(), key=lambda x: x[1])
            return {self.cursor_field: latest_record[0]}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        **kwargs
    ) -> Iterable[Mapping]:
        def __newer_than_latest(recorded_state: arrow.Arrow, latest_record: dict) -> bool:
            latest_record_date = arrow.get(latest_record["createdTime"])
            if recorded_state > latest_record_date:
                return False
            else:
                return True
        contents = response.json().get("data")
        if not contents:
            yield from []
        else:
            if stream_state:
                stored_date = arrow.get(stream_state[self.cursor_field])
                if __newer_than_latest(stored_date, contents[0]) is False:
                    yield from []
                else:
                    only_the_newest = [x for x in contents if __newer_than_latest(stored_date, x)]
                    yield from only_the_newest
            else:
                yield from contents


class ZohoDeskSubstream(ZohoDeskStream):
    @property
    def parent(self):
        return NotImplementedError

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        seen = []
        pr = self.parent(authenticator=self._session.auth)
        self.logger.info("Fetching tickets from parent stream...")
        pr_records = pr.read_records(sync_mode=SyncMode.full_refresh)

        self.logger.info("Sorting out unique department IDs...")
        for record in pr_records:
            if record["departmentId"] in seen:
                continue
            else:
                seen.append(record["departmentId"])

        self.logger.debug(f"unique ids: {seen}")

        self.logger.info("yielding results...")
        for dept_id in seen:
            self.logger.debug(f"yielding: {dept_id}")
            yield {"department_id": dept_id}
