from typing import Mapping, Any, Iterable

import requests

from .bases import RobinChildStream
from .parents import OrganizationUsers, OrganizationLocations

class OrganizationUsersData(RobinChildStream):
    parent_stream = OrganizationUsers
    path_template = "organizations/{organization_id}/users/{entity_id}"
    foreign_key = "id"
    foreign_key_name = "user_id"
    primary_key = "id"
    data_is_single_object = True

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


class Users(RobinChildStream):
    parent_stream = OrganizationUsers
    path_template = "users/{entity_id}"
    foreign_key = "id"
    foreign_key_name = "user_id"
    primary_key = "id"
    data_is_single_object = True


class UsersPresence(RobinChildStream):
    parent_stream = OrganizationUsers
    path_template = "users/{entity_id}/presence"
    foreign_key = "id"
    foreign_key_name = "user_id"
    primary_key = "id"
    data_is_single_object = False

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

class UsersEvents(RobinChildStream):
    parent_stream = OrganizationUsers
    path_template = "users/{entity_id}/events"
    foreign_key = "id"
    foreign_key_name = "user_id"
    primary_key = "id"
    data_is_single_object = False

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
            self.logger.info(f"No events records available for user: {slice['user_id']}")
            self.logger.debug(f"len(events) = {len(presence_data)}")
            yield from []

class Locations(RobinChildStream):
    parent_stream = OrganizationLocations
    path_template = "locations/{entity_id}"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "location_id"
    data_is_single_object = True

class LocationSpaces(RobinChildStream):
    parent_stream = OrganizationLocations
    path_template = "locations/{entity_id}/spaces"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "space_id"
    data_is_single_object = False

class LocationPresence(RobinChildStream):
    parent_stream = OrganizationLocations
    path_template = "locations/{entity_id}/presence"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "presence_id"
    data_is_single_object = False
