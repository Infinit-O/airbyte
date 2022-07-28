#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from math import inf
from urllib.parse import urljoin, urlparse

import requests
import pendulum

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Basic full refresh stream
class SignrequestStream(HttpStream, ABC):
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
    `class SignrequestStream(HttpStream, ABC)` which is the current class
    `class Customers(SignrequestStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(SignrequestStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalSignrequestStream((SignrequestStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    _path_name = ""
    @property
    def url_base(self):
        return urljoin(self.config["url_base"], "api/v1/")

    def __init__(self, config, *args, **kwargs):
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
        raw = response.json()
        next = raw.get("next", None)
        if next is not None:
            return {"next": next}
        else:
            return {}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if next_page_token:
            parts = urlparse(next_page_token["next"])
            return self._path_name + "?" + parts.query
        else:
            return self._path_name

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
        raw = response.json()
        yield from raw.get("results")

class SignrequestIncrementalStream(SignrequestStream, IncrementalMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        if current_stream_state == {}:
            self.state = latest_record[self.cursor_field]
            return {self.cursor_field: latest_record[self.cursor_field]}
        else:
            records = {}
            records[current_stream_state[self.cursor_field]] = pendulum.parse(current_stream_state[self.cursor_field])
            records[latest_record[self.cursor_field]] = pendulum.parse(latest_record[self.cursor_field])
            # NOTE: So there's an issue with the way mypy expects the types for max() and how I've done it here
            #       and I'm not sure how to resolve it.
            #       Argument 1 is simply supposed to be "iterable" as opposed to strictly
            #       Iterable[Mapping[str, Any]], I don't know if I just suck at type theory or if 
            #       this is really a bug.
            #       The code works fine in production.
            latest_record = max(records.items(), key=lambda x: x[1])
            self.state = latest_record[0]
            return {self.cursor_field: latest_record[0]}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        def __newer_than_latest(recorded_state: dict, latest_record: dict) -> bool:
            latest_record_date = pendulum.parse(latest_record[self.cursor_field])
            recorded_state = pendulum.parse(recorded_state[self.cursor_field])
            if recorded_state >= latest_record_date:
                return False
            else:
                return True

        raw = response.json()
        results = raw.get("results")
        if stream_state:
            if not __newer_than_latest(stream_state, results[0]):
                yield from []
            else:
                only_the_newest = [x for x in results if __newer_than_latest(stream_state, x)]
                yield from only_the_newest
        else:
            yield from results

class AuditEvents(SignrequestStream):
    primary_key = "user_uuid"
    _path_name = "audit-events/"

class TeamMembers(SignrequestStream):
    primary_key = "uuid"
    _path_name = "team-members/"

class Teams(SignrequestStream):
    primary_key = "uuid"
    _path_name = "teams/"

class Events(SignrequestIncrementalStream):
    primary_key = "uuid"
    cursor_field = "timestamp"

    _path_name = "events/"

class Documents(SignrequestStream):
    primary_key = "uuid"
    _path_name = "documents/"

class DocumentAttachments(SignrequestStream):
    primary_key = "uuid"
    _path_name = "document-attachments/"

class Templates(SignrequestStream):
    primary_key = "uuid"
    _path_name = "templates/"

class Signrequests(SignrequestStream):
    primary_key = "uuid"
    _path_name = "signrequests/"

    # @property
    # def cursor_field(self) -> str:
    #     return ""

# Source
class SourceSignrequest(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        access_token = config.get("access_token", None)
        if not access_token:
            return False, "NO ACCESS TOKEN PROVIDED, PLEASE CHECK CONFIG AND TRY AGAIN."
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        token = config.get("access_token")
        auth = TokenAuthenticator(token=token, auth_method="Token")  # Oauth2Authenticator is also available if you need oauth support
        return [
            AuditEvents(config=config, authenticator=auth),
            Documents(config=config, authenticator=auth),
            DocumentAttachments(config=config, authenticator=auth),
            Events(config=config, authenticator=auth),
            Signrequests(config=config, authenticator=auth),
            TeamMembers(config=config, authenticator=auth),
            Teams(config=config, authenticator=auth),
            Templates(config=config, authenticator=auth),
        ]
