from typing import Mapping, Any, MutableMapping, Iterable

import requests

from .base import JumpcloudV2Stream

class ActiveDirectory(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "activedirectories/"


class AuthnPolicy(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "authn/policies/"

class CustomEmailTemplates(JumpcloudV2Stream):
    primary_key = "type"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "customemail/templates/"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # NOTE: Stupid hack - customemail/templates/ does not support 'limit' and 'skip' params and will attempt to paginate
        #       endlessly, causing this stream to run forever.
        self.keep_going = False
        yield from response.json()

class Directories(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "directories/"
        
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # NOTE: Stupid hack - customemail/templates/ does not support 'limit' and 'skip' params and will attempt to paginate
        #       endlessly, causing this stream to run forever.
        self.keep_going = False
        yield from response.json()

class Groups(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "groups/"

class IPLists(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "iplists/"

class LDAPServers(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "ldapservers/"

class Policies(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "policies/"
    
class PolicyTemplates(JumpcloudV2Stream):
    # NOTE: This one seems to have 2 pages, response will be empty once you've hit the end;
    #       Need to figure out some way to do it.
    # TODO: Come back to this one and get pagination working!
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "policytemplates/"

class Subscriptions(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "subscriptions/"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # NOTE: Stupid hack - Subscriptions does not support 'limit' and 'skip' params and will attempt to paginate
        #       endlessly, causing this stream to run forever.
        self.keep_going = False
        yield from response.json()

class SystemGroups(JumpcloudV2Stream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "systemgroups/"