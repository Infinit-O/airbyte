from abc import abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .base_substream import ZohoRecruitSubStream
from .base import ZohoRecruitStream

class ModuleSettings(ZohoRecruitStream):
    primary_key = "id"
    envelope_name = "modules"

    def path(self, **kwargs):
        return "settings/modules"

class ModuleDetails(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "settings/modules/{module_api_name}"
    api_field_name= "api_name"
    envelope_name = "modules"

class ModuleFields(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "settings/fields?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "fields"

class ModuleLayouts(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "settings/layouts?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "layouts"

class RelatedLists(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "settings/related_lists?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "related_lists"

class ModuleRecords(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "{module_api_name}"
    api_field_name = "api_name"
    envelope_name = "data"

class ModuleRecordsDeleted(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "{module_api_name}/deleted"
    api_field_name = "api_name"
    envelope_name = "data"

class NoteTypes(ZohoRecruitStream):
    primary_key = "id"
    envelope_name = "note_types"
    
    def path(self, **kwargs):
        return "settings/note_types"

class Roles(ZohoRecruitStream):
    primary_key = "id"
    envelope_name = "roles"

    def path(self, **kwargs):
        return "settings/roles"

class Profiles(ZohoRecruitStream):
    primary_key = "id"
    envelope_name = "profiles"

    def path(self, **kwargs):
        return "settings/profiles"
        
class Org(ZohoRecruitStream):
    primary_key = "id"
    envelope_name = "org"

    def path(self, **kwargs):
        return "org"

class Users(ZohoRecruitStream):
    primary_key = "id"
    envelope_name = "users"

    def path(self, **kwargs):
        return "users"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        return {"type": "AllUsers"}
