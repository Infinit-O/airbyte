from typing import Any, Iterable, List, Mapping, Optional

import requests

from .bases import DesktopCentralStream, SummaryOverride, DesktopCentralThreatStream


class AllSystems(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "resource_id"
    envelope_name = "allsystems"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/allsystems"


class DeploymentPolicies(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "template_id"
    envelope_name = "deploymentpolicies"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/deploymentpolicies"


class LicenseSoftware(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "licensesoftware"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/licensesoftware"

class PatchSummary(SummaryOverride):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "summary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/summary"

class RemoteOffice(DesktopCentralStream):
    primary_key = "resource_id"
    envelope_name = "remoteoffice"
    
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/som/remoteoffice"

class ScanComputers(DesktopCentralStream):
    primary_key = "resource_id"
    envelope_name = "scancomputers"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/scancomputers"

class ScanDetails(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "resource_id"
    envelope_name = "scandetails"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/scandetails"


class SupportedPatches(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "patch_id"
    envelope_name = "supportedpatches"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/supportedpatches"

class ViewConfig(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "config_id"
    envelope_name = "viewconfig"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/viewconfig"
    
class ServerProperties(SummaryOverride):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "serverproperties"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/desktop/serverproperties"
    
class ApplicablePatches(DesktopCentralThreatStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "patches"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "dcapi/threats/patches"

class SystemPatchDetails(DesktopCentralThreatStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "systemreport"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "/dcapi/threats/systemreport/patches"
