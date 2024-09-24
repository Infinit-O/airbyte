from typing import Mapping, Any 

from .bases import SummaryOverride

class ApprovalSettings(SummaryOverride):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "approvalsettings"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/approvalsettings"

class AllSummary(SummaryOverride):
    primary_key = None
    envelope_name = "allsummary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/allsummary"

class DbUpdateStatus(SummaryOverride):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "dbupdatestatus"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/dbupdatestatus"

class Discover(SummaryOverride):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "discover"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/desktop/discover"

class FilterParams(SummaryOverride):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "filterparams"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/filterparams"

class HealthPolicy(SummaryOverride):
    # NOTE: Important note about this stream - as of today there isn't any data in our hosted
    #       instance so I can't work out the schema. Thus, the schema we've got right now is an
    #       empty object that covers basically anything that might be there. 
    primary_key = None
    envelope_name = "healthpolicy"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/patch/healthpolicy"

class Summary(SummaryOverride):
    # NOTE: This endpoint does not actually have a primary key it's just a summary
    #       of stats, and not a list of resources
    primary_key = None
    envelope_name = "summary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/som/summary"
