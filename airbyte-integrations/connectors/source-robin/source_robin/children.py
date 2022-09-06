from re import I
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

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

class OrganizationLocationEvents(RobinChildStream):
    parent_stream = OrganizationLocations
    path_template = "locations/{entity_id}/events"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "location_id"
    data_is_single_object = False

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["before"] = "2999-01-01T00:00:00Z"
        params["after"] = "2021-01-01T00:00:00Z"
        return params

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

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        self.logger.info("Stream 'spaces' has special handling for request_params. Adding 'include' param for calendar data.")
        params["include"] = "calendar"
        return params

class Reservations(RobinChildStream):
    parent_stream = OrganizationLocations
    path_template = "reservations/seats"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "location_id"
    data_is_single_object = False

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        self.logger.info("Stream 'spaces' has special handling for request_params. Adding 'include' param for calendar data.")
        params["location_ids"] = stream_slice[self.foreign_key_name]
        return params

class ReservationConfirmations(RobinChildStream):
    parent_stream = Reservations
    path_template = "reservations/seats/{entity_id}/confirmation"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "reservation_id"
    data_is_single_object = True
    # NOTE: 404 in Robin means that there's no data for the given <x>. Not necessarily
    #       that <x> is invalid, but that there's no data for it. Small distinction, but
    #       its important IMO.
    raise_on_http_errors = False

class ReservationInstances(RobinChildStream):
    parent_stream = Reservations
    path_template = "reservations/seats/{entity_id}/instances"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "reservation_id"
    data_is_single_object = False
    # NOTE: When reservation_id isn't recurring, it returns a 400.
    #       the 400 does not mean that the reservation_id is bad. 
    raise_on_http_errors = False

class SpaceAmenities(Spaces):
    path_template = "spaces/{entity_id}/amenities"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "amenity_id"
    data_is_single_object = False

class Events(RobinChildStream):
    parent_stream = OrganizationLocationEvents
    path_template = "events/{entity_id}"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "event_id"
    data_is_single_object = True
    raise_on_http_errors = False

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

class SeatAmenities(SpaceSeats):
    path_template = "seats/{entity_id}/amenities"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "seat_id"
    data_is_single_object = False
    raise_on_http_errors = False

class Zones(SpaceZones):
    path_template = "zones/{entity_id}"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "id"
    data_is_a_single_object = False
    raise_on_http_errors = False

class ZoneSeats(SpaceZones):
    path_template = "zones/{entity_id}/seats"
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "id"
    data_is_a_single_object = False
    raise_on_http_errors = False
