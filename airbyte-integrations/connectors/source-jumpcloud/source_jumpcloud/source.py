#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .v1 import (
    Applications,
    ApplicationTemplates,
    Systems,
    SystemUsers,
    CommandResults, 
    Commands,
    Organizations,
    RadiusServers
)
from .v2 import (
    ActiveDirectory,
    AuthnPolicy,
    CustomEmailTemplates,
    Directories,
    Groups,
    IPLists,
    LDAPServers,
    Policies,
    PolicyTemplates,
    Subscriptions,
    SystemGroups,
)

from .v2_systeminsights import (
    SystemInsightsALF,
    SystemInsightsALFExceptions,
    SystemInsightsApps,
    SystemInsightsAuthorizedKeys,
    SystemInsightsBattery,
    SystemInsightsBitlockerInfo,
    SystemInsightsBrowserPlugins,
    SystemInsightsCertificates,
    SystemInsightsChromeExtensions,
    SystemInsightsConnectivity,
    SystemInsightsCrashes,
    SystemInsightsCUPSDestinations,
    SystemInsightsDiskEncryption,
    SystemInsightsDiskInfo,
    SystemInsightsDNSResolvers,
    SystemInsightsETCHosts,
)

# Source
class SourceJumpcloud(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        api_token = config.get("api_key", "")
        if api_token == "":
            return False, "API key can't be an empty string!"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        v1 = [
            Applications(config=config),
            ApplicationTemplates(config=config),
            Systems(config=config),
            SystemUsers(config=config),
            CommandResults(config=config), 
            Commands(config=config),
            Organizations(config=config),
            RadiusServers(config=config),
        ]

        v2 = [
            ActiveDirectory(config=config),
            AuthnPolicy(config=config),
            CustomEmailTemplates(config=config),
            Directories(config=config),
            Groups(config=config),
            IPLists(config=config),
            LDAPServers(config=config),
            Policies(config=config),
            PolicyTemplates(config=config),
            Subscriptions(config=config),
            SystemGroups(config=config),
        ]

        system_insights = [
            SystemInsightsALF(config=config),
            SystemInsightsALFExceptions(config=config),
            SystemInsightsApps(config=config),
            SystemInsightsAuthorizedKeys(config=config),
            SystemInsightsBattery(config=config),
            SystemInsightsBitlockerInfo(config=config),
            SystemInsightsBrowserPlugins(config=config),
            SystemInsightsCertificates(config=config),
            SystemInsightsChromeExtensions(config=config),
            SystemInsightsConnectivity(config=config),
            SystemInsightsCrashes(config=config),
            SystemInsightsCUPSDestinations(config=config),
            SystemInsightsDiskEncryption(config=config),
            SystemInsightsDiskInfo(config=config),
            SystemInsightsDNSResolvers(config=config),
            SystemInsightsETCHosts(config=config),
        ]

        return v1 + v2 + system_insights
