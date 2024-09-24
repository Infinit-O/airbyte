#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .auth import OTPAuthenticator
from .stream_families import (
    AllPatches,
    AllPatchDetails,
    Computers,
    ComputerSummary,
    Hardware,
    HardwareInstallations,
    Software,
    SoftwareInstallations,
    SoftwareOnComputer,
    SystemReport,
    SoftwareMeteringComputers,
    AssociatedLicenses,
    SoftwareMeteringSummary,
    SoftwareAssociatedComputers
)
from .streams import (
    AllSystems,
    DeploymentPolicies,
    LicenseSoftware,
    PatchSummary,
    RemoteOffice,
    ScanComputers,
    ScanDetails,
    SupportedPatches,
    ViewConfig,
    ServerProperties,
    ApplicablePatches,
    SystemPatchDetails
    
)
from .stream_summaries import (
    AllSummary,
    ApprovalSettings,
    DbUpdateStatus,
    Discover,
    FilterParams,
    HealthPolicy,
    Summary,
)
from .stream_supported_patches import (
    SupportedPatchesUnrated,
    SupportedPatchesLow,
    SupportedPatchesModerate,
    SupportedPatchesImportant,
    SupportedPatchesCritical
)

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

# Source
class SourceEndpointCentral(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            apikey = config["apikey"]
            base_url = config["base_url"]
        except KeyError:
            return False, "apikey / base_url / missing from config file, please check and try again."

        auth = OTPAuthenticator(
            apikey=config["apikey"],
            base_url=config["base_url"]
        )

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = OTPAuthenticator(
            apikey=config["apikey"],
            base_url=config["base_url"]
        )
        return [
            AllPatches(authenticator=auth, config=config),
            AllPatchDetails(authenticator=auth, config=config),
            AllSummary(authenticator=auth, config=config),
            AllSystems(authenticator=auth, config=config),
            ApprovalSettings(authenticator=auth, config=config),
            Computers(authenticator=auth, config=config),
            ComputerSummary(authenticator=auth, config=config),
            DbUpdateStatus(authenticator=auth, config=config),
            DeploymentPolicies(authenticator=auth, config=config),
            Discover(authenticator=auth, config=config),
            FilterParams(authenticator=auth, config=config),
            Hardware(authenticator=auth, config=config),
            HardwareInstallations(authenticator=auth, config=config),
            HealthPolicy(authenticator=auth, config=config),
            #LicenseSoftware(authenticator=auth, config=config), ## No data
            PatchSummary(authenticator=auth, config=config),
            RemoteOffice(authenticator=auth, config=config),
            ScanComputers(authenticator=auth, config=config),
            ScanDetails(authenticator=auth, config=config),
            Software(authenticator=auth, config=config),
            SoftwareInstallations(authenticator=auth, config=config), # Big Data
            SoftwareMeteringSummary(authenticator=auth, config=config),
            SoftwareOnComputer(authenticator=auth, config=config), #Big Data
            Summary(authenticator=auth, config=config),
            SupportedPatches(authenticator=auth, config=config),
            SystemReport(authenticator=auth, config=config),
            ViewConfig(authenticator=auth, config=config),
            SoftwareMeteringComputers(authenticator=auth, config=config),
            #AssociatedLicenses(authenticator=auth, config=config), No Data
            #SoftwareAssociatedComputers(authenticator=auth, config=config), No Data
            ServerProperties(authenticator=auth, config=config),
            ApplicablePatches(authenticator=auth, config=config),
            SystemPatchDetails(authenticator=auth, config=config),    
            SupportedPatchesUnrated(authenticator=auth, config=config),
            SupportedPatchesLow(authenticator=auth, config=config),
            SupportedPatchesModerate(authenticator=auth, config=config),
            SupportedPatchesImportant(authenticator=auth, config=config),
            SupportedPatchesCritical(authenticator=auth, config=config)
        ]
