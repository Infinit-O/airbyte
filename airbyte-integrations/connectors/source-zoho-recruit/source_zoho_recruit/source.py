#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from tkinter import E
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator


# Basic full refresh stream
class ZohoRecruitStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class ZohoRecruitStream(HttpStream, ABC)` which is the current class
    `class Customers(ZohoRecruitStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ZohoRecruitStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalZohoRecruitStream((ZohoRecruitStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # TODO: Fill in the url base. Required.
    url_base = "https://recruit.zoho.com/recruit/v2/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        return {}

class ZohoRecruitSubStream(ZohoRecruitStream):
    @property
    @abstractmethod
    def path_template(self):
        pass

    @property
    @abstractmethod
    def parent_stream(self):
        pass

    @property
    @abstractmethod
    def api_field_name(self):
        pass

    @property
    def bad_api_list(self):
        pass
    
    @property
    def envelope_name(self):
        pass

    def stream_slices(self, **kwargs):
        items = self.parent_stream(authenticator=self._session.auth)
        for item in items.read_records(sync_mode=SyncMode.full_refresh):
            # NOTE: Zoho API throws an error when you try to get the module details
            #       for the "home" module
            #       apparently, it doesn't support a call to details
            if self.bad_api_list and item["api_name"].lower() in self.bad_api_list:
                continue
            else:
                yield {"module_api_name": item[self.api_field_name]}

    def path(self, stream_slice, **kwargs):
        streamslice = stream_slice or {}
        return self.path_template.format(module_api_name=streamslice["module_api_name"])

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        # NOTE: Workaround for the fact that Zoho APIs seem to return 204 no content
        #       in place of an empty JSON response 
        if response.status_code == 204:
            yield from []
        else:
            yield from response.json().get(self.envelope_name, [])

class Modules(ZohoRecruitStream):
    primary_key = "id"

    @property
    def use_cache(self):
        return True

    def path(self, **kwargs):
        return "settings/modules"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        yield from response.json().get("modules", [])

class ModuleDetails(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = Modules
    path_template = "settings/modules/{module_api_name}"
    api_field_name= "api_name"
    envelope_name = "modules"

    unsupported_api_list = ["home", "analytics", "emails", "documents", "social", "zoho_marketplace"]
    invalid_name_list = ["reports", "dashboards", "metrics",] 
    bad_api_list = unsupported_api_list + invalid_name_list

class ModuleFields(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = Modules
    path_template = "settings/fields?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "fields"

    unauthorized_api_list = ["referrals"]
    unsupported_api_list = ["home", "analytics", "emails", "documents", "social", "zoho_marketplace"]
    invalid_name_list = ["reports", "dashboards", "metrics",] 
    empty_api_list = ["approvals"]
    bad_api_list = unsupported_api_list + empty_api_list + unauthorized_api_list + invalid_name_list

class ModuleViews(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = Modules
    path_template = "settings/custom_views/{module_id}?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "custom_fields"

    unauthorized_api_list = ["referrals"]
    unsupported_api_list = ["home", "analytics", "emails", "documents", "social", "zoho_marketplace"]
    invalid_name_list = ["reports", "dashboards", "metrics",] 
    empty_api_list = ["approvals"]
    bad_api_list = unsupported_api_list + empty_api_list + unauthorized_api_list + invalid_name_list

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
    parent_stream = Modules
    path_template = "settings/layouts?module={module_api_name}"
    api_field_name = "api_name"
    envelope_name = "layouts"

    unauthorized_api_list = ["referrals"]
    unsupported_api_list = ["home", "analytics", "emails", "documents", "social", "zoho_marketplace"]
    invalid_name_list = ["reports", "dashboards", "metrics",] 
    empty_api_list = ["approvals"]
    bad_api_list = unsupported_api_list + empty_api_list + unauthorized_api_list + invalid_name_list

class NoteTypes(ZohoRecruitStream):
    primary_key = "id"
    
    def path(self, **kwargs):
        return "settings/note_types"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        yield from response.json().get("note_types", [])

class Roles(ZohoRecruitStream):
    primary_key = "id"

    def path(self, **kwargs):
        return "settings/roles"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        yield from response.json().get("roles", [])

class Profiles(ZohoRecruitStream):
    primary_key = "id"

    def path(self, **kwargs):
        return "settings/profiles"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        yield from response.json().get("profiles", [])
        
class Org(ZohoRecruitStream):
    primary_key = "id"

    def path(self, **kwargs):
        return "org"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        yield from response.json().get("org", [])

class Users(ZohoRecruitStream):
    primary_key = "id"

    def path(self, **kwargs):
        return "users"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        yield from response.json().get("users", [])

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        return {"type": "AllUsers"}

# NOTE: SAving this for reference later. I need the stream_slices method later.
class Employees():
    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")


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
            Modules(authenticator=auth),
            ModuleDetails(authenticator=auth),
            ModuleFields(authenticator=auth),
            ModuleViews(authenticator=auth),
            ModuleLayouts(authenticator=auth),
            NoteTypes(authenticator=auth),
            Roles(authenticator=auth),
            Profiles(authenticator=auth),
            Org(authenticator=auth),
            Users(authenticator=auth)
        ]
