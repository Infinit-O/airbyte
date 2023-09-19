#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from multiprocessing import AuthenticationError
from typing import Any, List, Mapping, MutableMapping, Tuple, Iterable, Optional

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .base import ZohoDeskStream
# TODO: FIX THIS LATER
from .clean import *
from .weird import *
from .dashboards import *
from .community_moderation import *


# Source
class SourceZohoDesk(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        oauth_id: str = config["client_id"]
        oauth_secret: str = config["client_secret"]
        oauth_refresh_token: str = config["refresh_token"]
        oauth_refresh_token_endpoint: str = config["token_refresh_endpoint"]
        if oauth_id == "":
            return False, "oAuth ID cannot be an empty string."
        if oauth_secret == "":
            return False, "oAuth secret cannot be an empty string."
        if oauth_refresh_token == "":
            return False, "oAuth refresh token cannot be an empty string."
        if oauth_refresh_token_endpoint == config["token_refresh_endpoint"] == "":
            return False, "oAuth refresh token endpoint cannot be an empty string."

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        auth = Oauth2Authenticator(
            token_refresh_endpoint=config["token_refresh_endpoint"],
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"]
            # scopes=config["oauth_scopes"] # this apparently can be ommitted....
        )
        return [
            Organizations(authenticator=auth),
            Agents(authenticator=auth),
            Profiles(authenticator=auth),
            Roles(authenticator=auth),
            Teams(authenticator=auth),
            Departments(authenticator=auth),
            Channels(authenticator=auth),
            Tickets(authenticator=auth),
            Contacts(authenticator=auth),
            Accounts(authenticator=auth),
            Modules(authenticator=auth),
            Countries(authenticator=auth),
            Languages(authenticator=auth),
            Timezones(authenticator=auth),
            TicketResolutionTime(authenticator=auth),
            TicketResponseTime(authenticator=auth),
            CommunityModerationCounts(authenticator=auth),
            CommunityTopicTypes(authenticator=auth),
            CommunityPreferences(authenticator=auth),
            AvailableBadgeIcons(authenticator=auth),
            RecycleBin(authenticator=auth),
            Users(authenticator=auth),
            BusinessHours(authenticator=auth),
            Tasks(authenticator=auth),
            ArchivedTickets(authenticator=auth),
        ]
