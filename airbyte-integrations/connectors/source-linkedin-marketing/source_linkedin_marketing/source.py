#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

from .bases import LinkedinMarketingStream


class LinkedinStandardDataStream(LinkedinMarketingStream):
    url_base = "https://api.linkedin.com/v2/"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        data = response.json()
        yield from data


class LinkedinAPIStream(LinkedinMarketingStream):
    url_base = "https://api.linkedin.com/rest/"


class OrganizationFollowerStatistics(LinkedinAPIStream):
    primary_key = "id"

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
        return {
            "q": "organizationalEntity",
            "organizationalEntity": f"urn:li:organization:{self.config['org_id']}"
        }

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url
        is https://example-api.com/v1/customers then this should return "customers". Required.
        """
        return "organizationalEntityFollowerStatistics"


class StandardRegionData(LinkedinStandardDataStream):
    parent_stream = OrganizationFollowerStatistics

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        ps = self.parent_stream(authenticator=self._session.auth, config=self.config)
        for record in ps.read_records():
            pass
    pass


# Source
class SourceLinkedinMarketing(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = Oauth2Authenticator(
            token_refresh_endpoint=config["refresh_url"],
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"]
        )
        return [
            OrganizationFollowerStatistics(authenticator=auth, config=config)
        ]
