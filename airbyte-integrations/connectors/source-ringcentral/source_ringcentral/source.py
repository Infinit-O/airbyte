#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlparse
from urllib.parse import parse_qs 

import requests
import ringcentral
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from ringcentral.platform import Platform
from airbyte_cdk.models import SyncMode

from ringcentral.http.client import Client
from ringcentral.http.api_exception import ApiException

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""

# NOTE: platform.get() is the entry into the ringcentral API
# NOTE: need to find where I Can just drop this in to get it to work
# NOTE: MEO is as follows 
#   = read_records() 
#   s-> self.request_headers() 
#   -> self._create_prepared_request() 
#   -> self.request_kwargs()
#   -> self._send_request()
# Lots to cover I guess


# Basic full refresh stream
class RingcentralStream(HttpStream, ABC):
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
    `class RingcentralStream(HttpStream, ABC)` which is the current class
    `class Customers(RingcentralStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(RingcentralStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalRingcentralStream((RingcentralStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # NOTE: This isn't strictly necessary anymore.
    url_base = ""

    def __init__(self, platform: Platform, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._platform = platform

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
        rjson = response.json()
        try:
            paging = rjson["paging"]
        except KeyError:
            return None

        try:
            current_page = int(paging["page"])
            last_page = int(paging["pageEnd"])
        except KeyError:
            return None

        if current_page < last_page:
            return {"next_page": int(current_page) + 1}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return {"page": next_page_token["page"]}
        else:
            return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        rjson = response.json()
        yield from rjson["records"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        next_page_token = None
        pagination_complete = False
        while not pagination_complete:
            path = self.path(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token
            )

            self.logger.debug(f"Using path: {path}")

            try:
                raw_response = self._platform.get(path)
                response = raw_response._response
            except ApiException as e:
                self.logger.info("No response from API.")
                self.logger.debug(f"Exception: {e}")
                response = None

            if not response:
                self.logger.info("Response is NONE, ending sync." )
                yield from []
                next_page_token = None
            else:
                yield from self.parse_response(response)
                next_page_token = self.next_page_token(response)


            if not next_page_token:
                pagination_complete = True


class IncrementalRingcentralStream(RingcentralStream):
    @property
    @abstractmethod
    def parent_stream(self):
        pass

    @property
    @abstractmethod
    def parent_stream_attr(self):
        pass

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(platform=self._platform)
        ps_slices = [
            x
            for x in ps.stream_slices(
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
                stream_state=stream_state
            )
        ]
        for slice in ps_slices:
            records = ps.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_state=stream_state,
                stream_slice=slice,
                cursor_field=cursor_field, 
            )
            for rec in records:
                yield {self.parent_stream_attr: rec[self.parent_stream_attr]}


class Extensions(RingcentralStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "/account/~/extension"

class CompanyCallLog(RingcentralStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "/account/~/call-log"

class CompanyDirectory(RingcentralStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "/account/~/directory/entries"

class IndividualCallLog(IncrementalRingcentralStream):
    parent_stream = CompanyDirectory
    primary_key = "id"
    parent_stream_attr = "extensionNumber"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        extension_number = stream_slice[self.parent_stream_attr]
        return f"/account/~/extension/{extension_number}/call-log"

class MessageStore(IncrementalRingcentralStream):
    parent_stream = CompanyDirectory
    primary_key = "id"
    parent_stream_attr = "extensionNumber"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        extension_number = stream_slice[self.parent_stream_attr]
        return f"/account/~/extension/{extension_number}/message-store"

# Source
class SourceRingcentral(AbstractSource):
    def _create_rc_platform(self, client_id: str, client_secret: str, client_server: str, jwt: str):
        sdk: ringcentral.SDK = ringcentral.SDK(
            client_id,
            client_secret,
            client_server,
        )
        platform: ringcentral.platform.Platform = sdk.platform()
        # NOTE: This already does the raise_for_status() inside
        platform.login(jwt=jwt)

        return platform

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        client_id: str = config["rc_client_id"]
        client_secret: str = config["rc_client_secret"]
        server_url: str = config["rc_server_url"]
        jwt: str = config["rc_jwt"]

        try:
            platform: ringcentral.platform.Platform = self._create_rc_platform(
                client_id=client_id,
                client_secret=client_secret,
                client_server=server_url,
                jwt=jwt
            )
        except requests.exceptions.HTTPError as e:
            logger.info("Could not log in with credentials provided!")
            logger.info("Check input and try again!")
            logger.debug(f"Exception: {e}")
            logger.debug(f"client_id: {client_id}")
            logger.debug(f"client_secret: {client_secret}")
            logger.debug(f"server_url: {server_url}")
            logger.debug(f"jwt: {jwt}")
            return False, "failed to log in."

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        client_id: str = config["rc_client_id"]
        client_secret: str = config["rc_client_secret"]
        server_url: str = config["rc_server_url"]
        jwt: str = config["rc_jwt"]
        platform: ringcentral.platform.Platform = self._create_rc_platform(
            client_id,
            client_secret,
            server_url,
            jwt,
        )
        return [
            Extensions(platform=platform),
            CompanyDirectory(platform=platform),
            CompanyCallLog(platform=platform),
            IndividualCallLog(platform=platform),
            MessageStore(platform=platform),
        ]
