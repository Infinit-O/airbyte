#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urljoin
import time
import json

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from requests.auth import AuthBase

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

class CookieAuthenticator(AuthBase):
    def __init__(self, config):
        self.username = config["username"]
        self.password = config["password"]
        self.raw_key = config["api_key"]
        self.url_base = urljoin(config["base_url"], "/api/v1/")

    def __call__(self, r):
        # NOTE: I'm not totally sure which function Airbyte expects at this point
        #       Airbyte SOURCE CODE says to use requests.auth.AuthBase now, which
        #       Requests docs says needs to have __call__ defined, but
        #       code snippets from the Airbyte team still use get_auth_header()
        # NOTE: I've decided to just implement both.
        # NOTE: Is it always JSESSIONID?
        cookie_jar = self.login()
        r.prepare_cookies(cookie_jar)
        return r

    def get_auth_header(self) -> Mapping[str, any]:
        cookie_jar = self.login()
        return {"Cookie": "; ".join([f"{k}={v}" for k, v in requests.dict_from_cookiejar(cookie_jar)])}

    def login(self) -> Mapping[str, any]:
        obfuscated = self.obfuscateApiKey(self.raw_key)
        
        body = {
            "username": self.username,
            "password": self.password,
            "apiKey": obfuscated["obfuscated_key"],
            "timestamp": obfuscated["timestamp"],
        }

        login_url = urljoin(self.url_base, "authenticatedSession")
        resp = requests.post(login_url, json=body)
        # NOTE: It's SUPER IMPORTANT THAT any non-200 response be discarded because
        #       a JSESSIONID is generated regardless of whether or not authentication
        #       succeeds. Passing this ID on in any future requests will cause them
        #       to fail, as its technically an invalid session ID.
        resp.raise_for_status()
        return resp.cookies

    def obfuscateApiKey(self, seed) -> Mapping[str, any]:
        """
        The Zscaler API requires that API keys be "obfuscated" in this manner. This snippet
        of code was taken straight from their documentation.

        :seed - str, represents the raw, unmodified API key from the admin console.

        returns a dictionary containing a timestamp and the obfuscated key.
        """
        now = int(time.time() * 1000)
        n = str(now)[-6:]
        r = str(int(n) >> 1).zfill(6)
        key = ""
        for i in range(0, len(str(n)), 1):
            key += seed[int(str(n)[i])]
        for j in range(0, len(str(r)), 1):
            key += seed[int(str(r)[j])+2]

        return {
            "timestamp": now,
            "obfuscated_key": key
        }

# Basic full refresh stream
class ZscalerStream(HttpStream, ABC):
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
    `class ZscalerStream(HttpStream, ABC)` which is the current class
    `class Customers(ZscalerStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ZscalerStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalZscalerStream((ZscalerStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    @property
    def url_base(self):
        # EXAMPLE: https://zsapi.zscaler.net/api/v1/authenticatedSession
        return urljoin(self.config["base_url"], "/api/v1/")

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config

        # # Zscaler API requires that the api key be obfuscated.
        # obfuscated = self.obfuscateApiKey(self.config["api_key"])
        # login_body = {
        #     "username": self.config["username"],
        #     "password": self.config["password"],
        #     "apiKey": obfuscated["obfuscated_key"],
        #     "timestamp": obfuscated["timestamp"]
        # }
        # login_url = urljoin(self.url_base, "authenticatedSession")
        # # NOTE: This should handle auth for the whole run, as Requests
        # #       will automatically track and send cookies with each request 
        # #       after this one.
        # resp = self._session.post(url=login_url, json=login_body)
        # # NOTE: Maybe raise_for_status() here?
        # resp.raise_for_status()

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
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json()

    def obfuscateApiKey(self, seed) -> Mapping[str, any]:
        """
        The Zscaler API requires that API keys be "obfuscated" in this manner. This snippet
        of code was taken straight from their documentation.

        :seed - str, represents the raw, unmodified API key from the admin console.

        returns a dictionary containing a timestamp and the obfuscated key.
        """
        now = int(time.time() * 1000)
        n = str(now)[-6:]
        r = str(int(n) >> 1).zfill(6)
        key = ""
        for i in range(0, len(str(n)), 1):
            key += seed[int(str(n)[i])]
        for j in range(0, len(str(r)), 1):
            key += seed[int(str(r)[j])+2]

        return {
            "timestamp": now,
            "obfuscated_key": key
        }

class AdminUsers(ZscalerStream):
    @property
    def primary_key(self):
        return "id"

    def path(self, stream_state, stream_slice, next_page_token):
        return "adminUsers/"

class DlpDictionaries(ZscalerStream):
    primary_key = "id"

    def path(self, stream_state, stream_slice, next_page_token):
        return "dlpDictionaries/"

class DlpEngines(ZscalerStream):
    primary_key = "id"

    def path(self, stream_state, stream_slice, next_page_token):
        return "dlpEngines/"

class DlpNotificationTemplates(ZscalerStream):
    primary_key = "id"

    def path(self, stream_state, stream_slice, next_page_token):
        return "dlpNotificationTemplates/"


# Source
class SourceZscaler(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        cookie_authenticator = CookieAuthenticator(config=config)
        return [
            AdminUsers(authenticator=cookie_authenticator, config=config),
            DlpDictionaries(authenticator=cookie_authenticator, config=config),
            DlpEngines(authenticator=cookie_authenticator, config=config),
            DlpNotificationTemplates(authenticator=cookie_authenticator, config=config),
        ]
