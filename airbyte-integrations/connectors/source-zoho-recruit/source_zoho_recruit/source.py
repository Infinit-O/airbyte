#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .associated_records import AssociatedRecords
from .streams_special import (
    ModuleDetails,
    ModuleFields,
    ModuleSettings,
    ModuleViews,
    Tags,
)
from .streams import (
    ModuleSettings,
    ModuleDetails,
    ModuleFields,
    ModuleLayouts,
    ModuleRecords,
    ModuleRecordsDeleted,
    NoteTypes,
    Org,
    Profiles,
    RelatedLists,
    Roles,
    Users,
)

# Source
class SourceZohoRecruit(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        fields = ["client_id", "client_secret", "refresh_token", "refresh_endpoint"]
        for x in fields:
            if config.get(x) == "":
                return False, f"{x} field cannot be empty, check config and try again."

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = Oauth2Authenticator(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
            token_refresh_endpoint=config["refresh_endpoint"]
        )
        return [
            AssociatedRecords(authenticator=auth),
            ModuleSettings(authenticator=auth),
            ModuleDetails(authenticator=auth),
            ModuleFields(authenticator=auth),
            ModuleViews(authenticator=auth),
            ModuleLayouts(authenticator=auth),
            ModuleRecords(authenticator=auth),
            ModuleRecordsDeleted(authenticator=auth),
            NoteTypes(authenticator=auth),
            Org(authenticator=auth),
            Profiles(authenticator=auth),
            RelatedLists(authenticator=auth),
            Roles(authenticator=auth),
            Tags(authenticator=auth),
            Users(authenticator=auth)
        ]
