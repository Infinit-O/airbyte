from typing import Mapping, Any, Iterable

import requests
import arrow

from .base import JumpcloudV2IncrementalStream

class SystemInsightsALF(JumpcloudV2IncrementalStream):
    primary_key = "system_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "systeminsights/alf/"

class SystemInsightsALFExceptions(JumpcloudV2IncrementalStream):
    primary_key = "system_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "systeminsights/alf/"

class SystemInsightsApps(JumpcloudV2IncrementalStream):
    primary_key = "system_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "systeminsights/apps/"

class SystemInsightsAuthorizedKeys(JumpcloudV2IncrementalStream):
    primary_key = "uid"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "systeminsights/authorized_keys/"

class SystemInsightsBattery(JumpcloudV2IncrementalStream):
    primary_key = "system_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "systeminsights/battery/"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.

        :return an iterable containing each record in the response
        """
        contents = response.json()
        if not contents:
            self.keep_going = False
            return None
        else:
            sorted_contents = sorted(contents, key=lambda x: arrow.get(x["collection_time"]))
            reversed_contents = reversed(sorted_contents)
            yield from reversed_contents