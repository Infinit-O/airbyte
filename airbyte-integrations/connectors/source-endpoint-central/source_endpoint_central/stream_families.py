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
    primary_key = None
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
    envelope_name = "computers"
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
    primary_key = None
    foreign_key = "resource_id"
    envelope_name = "compdetailssummary"
    path_template = "api/1.4/inventory/compdetailssummary?resid={entity_id}"

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
    
class SoftwareMeteringSummary(DesktopCentralStream):
    primary_key = "app_definition_id"
    envelope_name = "swmeteringsummary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/swmeteringsummary"
    
        
class SoftwareMeteringComputers(DesktopCentralSubstream):
    parent_stream = SoftwareMeteringSummary
    primary_key = "resource_id"
    foreign_key = "app_definition_id"
    envelope_name = "computers"
    path_template = "api/1.4/inventory/computers?swmeruleid={entity_id}"
    
class AssociatedLicenses(DesktopCentralSubstream):
    parent_stream = Software
    primary_key = None
    foreign_key = "software_id"
    envelope_name = "licenses"
    path_template = "api/1.4/inventory/licenses?swid={entity_id}"
        
class SoftwareAssociatedComputers(DesktopCentralSubstream):
    parent_stream = Software
    primary_key = None
    foreign_key = "software_id"
    envelope_name = None
    path_template = "api/1.4/inventory/computers?licswid={entity_id}"