from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from airbyte_cdk.models import SyncMode
from abc import abstractmethod

import requests

from .bases import RobinStream

class Amenities(RobinStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return f"organizations/{self.config['org_id']}/amenities"

class Organization(RobinStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return f"organizations/{self.config['org_id']}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield from [response.json()["data"]]


class OrganizationUsers(RobinStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return f"organizations/{self.config['org_id']}/users"


class OrganizationLocations(RobinStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return f"organizations/{self.config['org_id']}/locations"


class DeviceManifests(RobinStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return f"device-manifests/"


class SCIMBaseStream(RobinStream):
    # NOTE: The SCIM endpoints have a completely different JSON envelope structure
    #       and a completely different pagination scheme! So I need to RE-DO the spider base here.
    primary_key = "id"
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        data = response.json()
        
        # NOTE: This is a bit messy; I'd like to fix it up later properly, but for now it will do
        try:
            total_results = data["totalResults"]
            start_index = data["startIndex"]
            items_per_page = data["itemsPerPage"]
        except KeyError:
            return None

        self.logger.debug(f"index {start_index} of {total_results} @ {items_per_page} per page.")

        if (start_index + items_per_page) < total_results:
            return {
                "totalResults": total_results,
                "startIndex": start_index,
                "itemsPerPage": items_per_page
            }
        else:
            return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            current_index = int(next_page_token["startIndex"])
            items_per_page = int(next_page_token["itemsPerPage"])
            new_index = current_index + items_per_page
            return {"startIndex": new_index}
        else:
            return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        resp = response.json()
        yield from resp["Resources"]

class SCIMChildStream(SCIMBaseStream):
    @property
    @abstractmethod
    def parent_stream(self):
        pass

    @property
    @abstractmethod
    def path_template(self):
        pass

    @property
    @abstractmethod
    def foreign_key(self):
        pass

    @property
    @abstractmethod
    def foreign_key_name(self):
        pass

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        user_id = stream_slice[self.foreign_key_name]
        final_path = self.path_template.format(entity_id=user_id)
        self.logger.debug(f"Path formed for: {self.path_template.format(entity_id=user_id)}")
        return final_path

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(authenticator=self._authenticator, config=self.config)
        for x in ps.read_records(SyncMode.full_refresh):
            s_slice = {self.foreign_key_name: x[self.foreign_key]}
            self.logger.debug(f"slice -> {s_slice}")
            yield {self.foreign_key_name: x[self.foreign_key]}

class SCIMUsers(SCIMBaseStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return f"scim-2/Users/"

class SCIMSpecificUser(SCIMChildStream):
    parent_stream = SCIMUsers
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "user_id"
    path_template = "scim-2/Users/{entity_id}"

    def parse_response(
        self,
        response: requests.Response,
        **kwargs
    ):
        data = response.json()
        yield from [data]

class SCIMGroups(SCIMBaseStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return f"scim-2/Groups/"

class SCIMSpecificGroup(SCIMChildStream):
    parent_stream = SCIMGroups
    primary_key = "id"
    foreign_key = "id"
    foreign_key_name = "user_id"
    path_template = "scim-2/Groups/{entity_id}"

    def parse_response(
        self,
        response: requests.Response,
        **kwargs
    ):
        data = response.json()
        yield from [data]
