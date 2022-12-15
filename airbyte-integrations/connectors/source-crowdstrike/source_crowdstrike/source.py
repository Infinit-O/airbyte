#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""

class CrowdstrikeOauth2Authenticator(Oauth2Authenticator):
    # NOTE: IMPORTANT! we can't use the 'refresh_token' grant...
    def get_refresh_request_body(self) -> Mapping[str, Any]:
        """Override to define additional parameters"""
        payload: MutableMapping[str, Any] = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        if self.scopes:
            payload["scopes"] = self.scopes

        return payload

# Basic full refresh stream
class CrowdstrikeStream(HttpStream, ABC):
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
    `class CrowdstrikeStream(HttpStream, ABC)` which is the current class
    `class Customers(CrowdstrikeStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(CrowdstrikeStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalCrowdstrikeStream((CrowdstrikeStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # TODO: Fill in the url base. Required.
    url_base = "https://api.us-2.crowdstrike.com"

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
        data = response.json()
        try:
            pagination = data["meta"]["pagination"]
        except KeyError:
            return None

        offset = pagination["offset"] 
        total = pagination["total"]
        limit = pagination["limit"]

        # NOTE: hardcoded to 10k for now. Crowdstrike has dumb limits.
        if offset != 9000:
            return {"offset": offset + limit}

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return {
                "limit": 1000,
                "offset": next_page_token["offset"]
            }
        return {"limit": 1000}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        data = response.json()
        resources = data["resources"]
        for x in resources:
            yield {"id": x}

class Detects(CrowdstrikeStream):
    primary_key = "trace_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "/detects/queries/detects/v1"
        

class DetectsInfo(CrowdstrikeStream):
    cursor_field = "na"
    primary_key = "na"

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        self.logger.info(f"stream slice: {stream_slice}")
        c_id = stream_slice["id"]
        ids = []
        ids.append(c_id)
        self.logger.info(f"ids: {ids}")
        return {
            "ids": ids
        }

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "detects/entities/summaries/GET/v1/"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        ps = Detects(authenticator=self.authenticator)


        for x in ps.read_records(sync_mode=SyncMode.full_refresh):
            self.logger.info(f"from stream slices, yielding x: {x['id']}")
            yield x

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        data = response.json()
        resources = data["resources"]
        for x in resources:
            yield x

# Source
class SourceCrowdstrike(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            secret = config["client_secret"]
            client_id = config["client_id"]
            refresh_endpoint = config["token_refresh_endpoint"]
            auth = CrowdstrikeOauth2Authenticator(
                client_id=client_id,
                client_secret=secret,
                refresh_token=None,
                token_refresh_endpoint=refresh_endpoint
            )  # Oauth2Authenticator is also available if you need oauth support
            token = auth.refresh_access_token()
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        secret = config["client_secret"]
        client_id = config["client_id"]
        refresh_endpoint = config["token_refresh_endpoint"]
        auth = CrowdstrikeOauth2Authenticator(
            client_id=client_id,
            client_secret=secret,
            refresh_token="asdf",
            token_refresh_endpoint=refresh_endpoint
        )  # Oauth2Authenticator is also available if you need oauth support
        return [DetectsInfo(authenticator=auth)]
