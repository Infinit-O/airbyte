#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from time import sleep

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""

class ReplacementTokenAuthenticator(TokenAuthenticator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # NOTE: I know that this is deprecated but this is the fastest
    #       way to do things.
    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"{self.auth_method}{self._token}"}


# Basic full refresh stream
class ClickupStream(HttpStream, ABC):
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
    `class ClickupStream(HttpStream, ABC)` which is the current class
    `class Customers(ClickupStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ClickupStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalClickupStream((ClickupStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://api.clickup.com/api/v2/"

    def _send(self, *args, **kwargs):
        sleep_time = 3
        self.logger.debug("Calling into overridden _send()")
        sleep(sleep_time)
        self.logger.debug(f"sleep is at {sleep_time}")
        return super()._send(*args, **kwargs)

    @property
    def entity_name(self):
        raise NotImplementedError

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
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        data = response.json()
        contents = data[self.entity_name]
        yield from contents

class ClickupSubStream(ClickupStream):
    @property
    def parent(self):
        raise NotImplementedError

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        # parent_stream_slices = self.parent.stream_slices(
        #     sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        # )
        parent = self.parent(authenticator=self.authenticator)

        parent_slices = parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        # for stream_slice in parent_stream_slices:
        for slice in parent_slices:
            for record in parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state,
                stream_slice=slice
            ):
                yield {"parent": record}

class Teams(ClickupStream):
    primary_key = "id"
    entity_name = "teams"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "team/"

class Spaces(ClickupSubStream):
    primary_key = "id"
    parent = Teams
    entity_name= "spaces"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        team_id = stream_slice["parent"]["id"]
        return f"team/{team_id}/space"
    
class Tags(ClickupSubStream):
    primary_key = "id"
    parent = Teams
    entity_name = "Tags"
    raise_on_http_errors = False

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        team_id = stream_slice["parent"]["id"]
        return f"space/{team_id}/tag"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        data = response.json()
        try:
            contents = data[self.entity_name]
            yield from contents
        except KeyError:
            yield from []

class Folders(ClickupSubStream):
    primary_key = "id"
    parent = Spaces
    entity_name = "folders"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        team_id = stream_slice["parent"]["id"]
        return f"space/{team_id}/folder"

class Lists(ClickupSubStream):
    primary_key = "id"
    parent = Folders
    entity_name = "lists"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        team_id = stream_slice["parent"]["id"]
        return f"folder/{team_id}/list"
    
class Tasks(ClickupSubStream):
    primary_key = "id"
    parent = Lists
    entity_name = "tasks"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        team_id = stream_slice["parent"]["id"]
        return f"list/{team_id}/task"

class Comments(ClickupSubStream):
    primary_key = "id"
    parent = Tasks 
    entity_name = "comments"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        team_id = stream_slice["parent"]["id"]
        return f"task/{team_id}/comment"

# Source
class SourceClickup(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        api_token = config["api_token"]
        headers = {"Authorization": f"{api_token}"}
        simple_request = requests.get("https://api.clickup.com/api/v2/team", headers=headers)
        simple_request.raise_for_status()

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        api_key = config["api_token"]
        auth = ReplacementTokenAuthenticator(token=api_key, auth_method="")  
        return [
            Teams(authenticator=auth),
            Spaces(authenticator=auth),
            Folders(authenticator=auth),
            Lists(authenticator=auth),
            Tasks(authenticator=auth),
            Comments(authenticator=auth),
            Tags(authenticator=auth),
        ]
