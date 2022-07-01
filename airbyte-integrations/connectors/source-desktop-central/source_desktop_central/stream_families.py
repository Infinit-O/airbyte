from typing import Mapping, Any, Iterable

import requests

from .bases import DesktopCentralStream, DesktopCentralSubstream

class Software(DesktopCentralStream):
    primary_key = "software_id"
    envelope_name = "software"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/software"

class SoftwareInstallations(DesktopCentralSubstream):
    parent_stream = Software
    # NOTE: primary_key here refers to the key of the CHILD stream
    primary_key = "resource_id"
    # NOTE: foreign key here refers to the key of the PARENT stream
    foreign_key = "software_id"
    envelope_name = "computers"
    path_template = "api/1.4/inventory/computers?swid={entity_id}"

class Hardware(DesktopCentralStream):
    primary_key = "resource_id"
    envelope_name = "hardware"
    
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/hardware"

class HardwareInstallations(DesktopCentralSubstream):
    parent_stream = Hardware
    primary_key = "resource_id"
    foreign_key = "hardware_id"
    envelope_name = "hardware"
    path_template = "api/1.4/inventory/computers?hwid={entity_id}"

class Computers(DesktopCentralStream):
    primary_key = "resource_id"
    envelope_name = "computers"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/som/computers"

class ComputerSummary(DesktopCentralSubstream):
    parent_stream = Computers
    primary_key = "na"
    foreign_key = "resource_id"
    envelope_name = "compdetailssummary"
    path_template = "api/1.4/inventory/compdetailssummary?resid={entity_id}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        # NOTE: This endpoint, like the other "summary" endpoints will only ever return a single object, rather
        #       than a list, so we handle it like this to keep airbyte from complaining
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

class SoftwareOnComputer(DesktopCentralSubstream):
    parent_stream = Computers
    primary_key = "software_id"
    foreign_key = "resource_id"
    envelope_name = "installedsoftware"
    path_template = "api/1.4/inventory/installedsoftware?resid={entity_id}"

class SystemReport(DesktopCentralSubstream):
    parent_stream = Computers
    primary_key = "patch_id"
    foreign_key = "resource_id"
    envelope_name = "systemreport"
    path_template = "api/1.4/patch/systemreport?resid={entity_id}"

class AllPatches(DesktopCentralStream):
    primary_key = "patch_id"
    envelope_name = "allpatches"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/allpatches"

class AllPatchDetails(DesktopCentralSubstream):
    parent_stream = AllPatches
    primary_key = "resource_id"
    foreign_key = "patch_id"
    envelope_name = "allpatchdetails"
    path_template = "api/1.4/patch/allpatchdetails?patchid={entity_id}"
