#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

# TODO: fix later.
from .parents import *
from .children import *
"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


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
            DeviceManifests(authenticator=auth, config=config),
            Locations(authenticator=auth, config=config),
            LocationSpaces(authenticator=auth, config=config),
            LocationPresence(authenticator=auth, config=config),
            Organization(authenticator=auth, config=config),
            OrganizationLocations(authenticator=auth, config=config),
            OrganizationUsers(authenticator=auth, config=config),
            OrganizationUsersData(authenticator=auth, config=config),
            SCIMGroups(authenticator=auth, config=config),
            SCIMSpecificUser(authenticator=auth, config=config),
            SCIMUsers(authenticator=auth, config=config),
            Spaces(authenticator=auth, config=config),
            SpaceAmenities(authenticator=auth, config=config),
            SpaceDevices(authenticator=auth, config=config),
            SpacePresence(authenticator=auth, config=config),
            SpaceSeats(authenticator=auth, config=config),
            SpaceState(authenticator=auth, config=config),
            SpaceZones(authenticator=auth, config=config),
            SeatAmenities(authenticator=auth, config=config),
            Users(authenticator=auth, config=config),
            # NOTE: UserEvents is disabled because I need more information
            #       on param format! needs either "before" or "after", but
            #       I don't know what it's supposed to look like.
            # NOTE: Other "events" streams are disabled for the same reason.
            # UsersEvents(authenticator=auth, config=config),
            UsersPresence(authenticator=auth, config=config),
            Zones(authenticator=auth, config=config),
            ZoneSeats(authenticator=auth, config=config),
        ]
