#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .bases import RobinStream

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


class Amenities(RobinStream):
    primary_key = "id"

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
        return f"organizations/{self.config['org_id']}/amenities"

class Organization(RobinStream):
    primary_key = "id"

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
        return f"organizations/{self.config['org_id']}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield from [response.json()["data"]]


class OrganizationUsers(RobinStream):
    primary_key = "id"

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
        return f"organizations/{self.config['org_id']}/users"


class OrganizationLocations(RobinStream):
    primary_key = "id"

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
        return f"organizations/{self.config['org_id']}/locations"


class OrganizationUsersData(RobinStream):
    parent_stream = OrganizationUsers
    path_template = "organizations/{organization_id}/users/{entity_id}"
    primary_key = "id"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(authenticator=self._authenticator, config=self.config)
        for x in ps.read_records(SyncMode.full_refresh):
            yield {"user_id": x["id"]}

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
        org_id = self.config["org_id"]
        user_id = stream_slice["user_id"]
        return self.path_template.format(entity_id=user_id, organization_id=org_id)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        resp = response.json()
        yield from [resp["data"]]

class Users(RobinStream):
    parent_stream = OrganizationUsers
    path_template = "users/{entity_id}"
    primary_key = "id"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(authenticator=self._authenticator, config=self.config)
        for x in ps.read_records(SyncMode.full_refresh):
            yield {"user_id": x["id"]}

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
        user_id = stream_slice["user_id"]
        return self.path_template.format(entity_id=user_id)

    # NOTE: REFACTOR ALL THIS LATER!!!
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        resp = response.json()
        yield from [resp["data"]]


class UsersPresence(RobinStream):
    parent_stream = OrganizationUsers
    path_template = "users/{entity_id}/presence"
    primary_key = "id"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(authenticator=self._authenticator, config=self.config)
        for x in ps.read_records(SyncMode.full_refresh):
            yield {"user_id": x["id"]}

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
        user_id = stream_slice["user_id"]
        return self.path_template.format(entity_id=user_id)

    # NOTE: REFACTOR ALL THIS LATER!!!
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        resp = response.json()
        slice = kwargs["stream_slice"]
        presence_data = resp["data"]
        if presence_data:
            for x in presence_data:
                x["user_id"] = slice["user_id"]
                yield x
        else:
            self.logger.info(f"No presence records available for user: {slice['user_id']}")
            self.logger.debug(f"len(presence_data) = {len(presence_data)}")
            yield from []

class UsersEvents(RobinStream):
    parent_stream = OrganizationUsers
    path_template = "users/{entity_id}/events"
    primary_key = "id"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(authenticator=self._authenticator, config=self.config)
        for x in ps.read_records(SyncMode.full_refresh):
            yield {"user_id": x["id"]}

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
        user_id = stream_slice["user_id"]
        return self.path_template.format(entity_id=user_id)

    # NOTE: REFACTOR ALL THIS LATER!!!
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        resp = response.json()
        slice = kwargs["stream_slice"]
        presence_data = resp["data"]
        if presence_data:
            for x in presence_data:
                x["user_id"] = slice["user_id"]
                yield x
        else:
            self.logger.info(f"No presence records available for user: {slice['user_id']}")
            self.logger.debug(f"len(presence_data) = {len(presence_data)}")
            yield from []


# Source
class SourceRobin(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(token=config["api_key"], auth_method="Access-Token")  # Oauth2Authenticator is also available if you need oauth support
        return [
            Amenities(authenticator=auth, config=config),
            Organization(authenticator=auth, config=config),
            OrganizationLocations(authenticator=auth, config=config),
            OrganizationUsers(authenticator=auth, config=config),
            OrganizationUsersData(authenticator=auth, config=config),
            Users(authenticator=auth, config=config),
            UsersPresence(authenticator=auth, config=config),
        ]
