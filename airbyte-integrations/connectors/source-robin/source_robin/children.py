from typing import Any, Iterable, List, Mapping, Optional

import requests
from airbyte_cdk.models import SyncMode

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

class Spaces(RobinChildStream):
    # NOTE: This is a special case; spaces are
    #       from the LocationSpaces stream, but
    #       LocationSpaces are themselves drawn from
    #       the OrganizationLocations stream.
    #       Child streams cannot themselves be parent streams
    #       I'm limited by how Airbyte chooses to model
    #       APIs
    parent_stream = LocationSpaces
    path_template = "spaces/{entity_id}"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "space_id"
    data_is_single_object = True

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ls = self.parent_stream(authenticator=self._authenticator, config=self.config)
        ls_slices = ls.stream_slices(SyncMode.full_refresh, cursor_field, stream_state)

        for slice in ls_slices:
            for record in ls.read_records(SyncMode.full_refresh, stream_slice=slice):
                yield {
                    self.foreign_key_name: record[self.foreign_key]
                }

class SpaceAmenities(Spaces):
    path_template = "spaces/{entity_id}/amenities"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "amenity_id"
    data_is_single_object = False

class SpacePresence(Spaces):
    path_template = "spaces/{entity_id}/presence"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "presence_id"
    data_is_single_object = False

class SpaceDevices(Spaces):
    path_template = "spaces/{entity_id}/devices"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "device_id"
    data_is_single_object = False

class SpaceState(Spaces):
    path_template = "spaces/{entity_id}/state"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "state_id"
    data_is_single_object = True

class SpaceSeats(Spaces):
    path_template = "spaces/{entity_id}/seats"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "seat_id"
    data_is_single_object = False 

class SpaceZones(Spaces):
    path_template = "spaces/{entity_id}/zones"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "zone_id"
    data_is_single_object = False 
