#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from requests.auth import AuthBase
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .community import Admins

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream

class AbstractParamsAuthenticator(AuthBase):
    """Abstract class for an header-based authenticators that add a header to outgoing HTTP requests."""

    def __call__(self, request):
        """Attach the HTTP headers required to authenticate on the HTTP request"""
        request.prepare_url(request.url, self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        """The header to set on outgoing HTTP requests"""

        return {self.param_name: self.token}

    @property
    @abstractmethod
    def token(self) -> str:
        """The header value to set on outgoing HTTP requests"""

    @property
    @abstractmethod
    def param_name(self) -> str:
        """The header value to set on outgoing HTTP requests"""

class FBParamAuthenticator(AbstractParamsAuthenticator):
    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, value):
        self._token = value

    @property
    def param_name(self):
        return "access_token"

    def __init__(self, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token

# Source
class SourceWorkplaceByMeta(AbstractSource):
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
        Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = FBParamAuthenticator(token=config.get("access_token"))  # Oauth2Authenticator is also available if you need oauth support
        return [
            Admins(authenticator=auth),
        ]
