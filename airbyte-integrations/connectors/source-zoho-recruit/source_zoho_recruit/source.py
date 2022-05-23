#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .base import ZohoRecruitStream
from .base_substream import ZohoRecruitSubStream


class ModuleSettings(ZohoRecruitStream):
    primary_key = "id"
    envelope_name = "modules"

    # @property
    # def use_cache(self):
    #     return True

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
        return self.path_template.format(
            module_id=streamslice["module_id"],
            module_api_name=streamslice["module_api_name"]
        )

class ModuleLayouts(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    path_template = "settings/layouts?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "layouts"

class ModuleAssociatedRecords(ZohoRecruitSubStream):
    pass

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
            yield response.json()

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

# Source
class SourceZohoRecruit(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        fields = ["client_id", "client_secret", "refresh_token", "refresh_endpoint"]
        for x in fields:
            if config.get(x) == "":
                return False, f"{x} field cannot be empty, check config and try again."

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = Oauth2Authenticator(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
            token_refresh_endpoint=config["refresh_endpoint"]
        )
        return [
            ModuleSettings(authenticator=auth),
            ModuleDetails(authenticator=auth),
            ModuleFields(authenticator=auth),
            ModuleViews(authenticator=auth),
            ModuleLayouts(authenticator=auth),
            ModuleRecords(authenticator=auth),
            ModuleRecordsDeleted(authenticator=auth),
            NoteTypes(authenticator=auth),
            Org(authenticator=auth),
            Profiles(authenticator=auth),
            RelatedLists(authenticator=auth),
            Roles(authenticator=auth),
            Tags(authenticator=auth),
            Users(authenticator=auth)
        ]
