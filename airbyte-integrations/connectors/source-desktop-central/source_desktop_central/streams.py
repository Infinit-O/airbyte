from typing import Any, Iterable, List, Mapping, Optional

import requests

from .bases import DesktopCentralStream

class ApprovalSettings(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "na"
    envelope_name = "approvalsettings"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/approvalsettings"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

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

class AllSummary(DesktopCentralStream):
    primary_key = "na"
    envelope_name = "allsummary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/allsummary"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

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

class DbUpdateStatus(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "na"
    envelope_name = "dbupdatestatus"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/dbupdatestatus"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

class Discover(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "na"
    envelope_name = "discover"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/desktop/discover"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

class FilterParams(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "na"
    envelope_name = "filterparams"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/filterparams"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

class HealthPolicy(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "na"
    envelope_name = "healthpolicy"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/healthpolicy"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

class LicenseSoftware(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "na"
    envelope_name = "licensesoftware"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/licensesoftware"

class PatchSummary(DesktopCentralStream):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = "na"
    envelope_name = "summary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/summary"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

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

class SoftwareMeteringSummary(DesktopCentralStream):
    primary_key = "na"
    envelope_name = "swmeteringsummary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """

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

class Summary(DesktopCentralStream):
    # NOTE: This endpoint does not actually have a primary key it's just a summary
    #       of stats, and not a list of resources
    primary_key = "na"
    envelope_name = "summary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/som/summary"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]


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
