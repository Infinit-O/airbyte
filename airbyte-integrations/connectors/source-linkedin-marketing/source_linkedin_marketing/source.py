#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, MutableMapping, Tuple
import time

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

from .bases import LinkedinMarketingStream


class CustomAuthWithDelay(Oauth2Authenticator):

    def get_auth_header(self) -> Mapping[str, Any]:
        """ This method overridden to add a delay, at the suggestion of LinkedIn dev support. """
        token = self.get_access_token()
        time.sleep(15)
        return {"Authorization": f"Bearer {token}"}


class LinkedinStandardDataStream(LinkedinMarketingStream):
    url_base = "https://api.linkedin.com/v2/"

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
            "locale.language": "en",
            "locale.country": "US"
        }


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


class OrganizationShareStatistics(LinkedinAPIStream):
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
        return "organizationalEntityShareStatistics"


class OrganizationPageStatistics(LinkedinAPIStream):
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
            "q": "organization",
            "organization": f"urn:li:organization:{self.config['org_id']}"
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
        return "organizationPageStatistics"


class StandardRegionData(LinkedinStandardDataStream):
    primary_key = "id"

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
        return "regions/"


class StandardCountryData(LinkedinStandardDataStream):
    primary_key = "$URN"

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
        return "countries/"


class StandardFunctionData(LinkedinStandardDataStream):
    primary_key = "id"

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
        return "functions/"


class StandardIndustryData(LinkedinStandardDataStream):
    primary_key = "id"

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
        return "industries/"


class StandardSeniorityData(LinkedinStandardDataStream):
    primary_key = "id"

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
        return "seniorities/"


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
        required_keys = [
            "client_id",
            "client_secret",
            "refresh_token",
            "refresh_url",
            "org_id",
            "linkedin_version"
        ]

        for x in required_keys:
            if x not in config.keys():
                return False, f"Missing {x} from config file."
            if not config[x]:
                return False, f"Value for key {x} is blank in config file, please check and try again."

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = CustomAuthWithDelay(
            token_refresh_endpoint=config["refresh_url"],
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"]
        )
        return [
            OrganizationFollowerStatistics(authenticator=auth, config=config),
            OrganizationPageStatistics(authenticator=auth, config=config),
            OrganizationShareStatistics(authenticator=auth, config=config),
            StandardCountryData(authenticator=auth, config=config),
            StandardFunctionData(authenticator=auth, config=config),
            StandardIndustryData(authenticator=auth, config=config),
            StandardRegionData(authenticator=auth, config=config),
            StandardSeniorityData(authenticator=auth, config=config),
        ]
