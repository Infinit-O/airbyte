from typing import Any, Iterable, List, Mapping, Optional

import requests

from .bases import DesktopCentralStream 

class SupportedPatchesUnrated(DesktopCentralStream):
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
        return "api/1.4/patch/supportedpatches?severityfilter=0"

class SupportedPatchesLow(DesktopCentralStream):
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
        return "api/1.4/patch/supportedpatches?severityfilter=1"
    
class SupportedPatchesModerate(DesktopCentralStream):
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
        return "api/1.4/patch/supportedpatches?severityfilter=2"

class SupportedPatchesImportant(DesktopCentralStream):
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
        return "api/1.4/patch/supportedpatches?severityfilter=3"
    
class SupportedPatchesCritical(DesktopCentralStream):
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
        return "api/1.4/patch/supportedpatches?severityfilter=4"
    
    
