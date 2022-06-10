from abc import abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .base_substream import ZohoRecruitSubStream
from .streams import ModuleSettings, ModuleDetails, ModuleFields

class ModuleViews(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "settings/custom_views/{module_id}?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "custom_fields"

    # NOTE: Overridden here because we need both the name AND the id to get this done.
    def stream_slices(self, **kwargs):
        items = self.parent_stream(authenticator=self._session.auth)
        for item in items.read_records(sync_mode=SyncMode.full_refresh):
            if self.bad_api_list and item[self.api_field_name].lower() in self.bad_api_list:
                continue
            else:
                yield {
                    "module_api_name": item[self.api_field_name],
                    "module_id": item["id"]
                }

    def path(self, stream_slice, **kwargs):
        streamslice = stream_slice or {}
        endpath = self.path_template.format(
            module_id=streamslice["module_id"],
            module_api_name=streamslice["module_api_name"]
        )
        return endpath

class Tags(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "settings/tags?module={module_api_name}"
    api_field_name = "api_name"

    # NOTE: Overridden here because of inconsistent data envelope shape; 
    #       does not return an array of objects like others
    #       instead it returns a single JSON object. if the return type is not an iterable,
    #       airbyte will fail.
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        if response.status_code == 204:
            yield from []
        else:
            yield response.json()["tags"]
