#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from base64 import urlsafe_b64encode
from urllib.parse import urljoin

import requests
import pyotp
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

class OTPAuthenticator(HttpAuthenticator):
    def __init__(self, username=None, password=None, base_url=None, otp_key=None, *args, **kwargs):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.LOGIN_URL = "/api/1.4/desktop/authentication"
        self.TWO_FACTOR_URL = "/api/1.4/desktop/authentication/otpValidate"
        self._totp = pyotp.TOTP(otp_key)
        self._auth_token = self.login()

    def login(self):
        # NOTE: Auth with Desktop Central occurs in 2 steps
        #       First, pass username and b64encoded password to auth endpoint
        #       Second, validate with OTP if needed
        b64_password = str(urlsafe_b64encode(bytes(self.password, "utf-8")), "utf-8")
        request_body = {
            "username": self.username,
            "password": b64_password,
            "auth_type": "local_authentication"
        }
        target_url = urljoin(self.base_url, self.LOGIN_URL)
        resp = requests.post(target_url, json=request_body, verify=False)
        resp.raise_for_status()

        resp = resp.json()

        try:
            two_factor = resp["message_response"]["authentication"]["two_factor_data"]
        except KeyError:
            two_factor = resp["message_response"]["authentication"]["auth_data"]["auth_token"]

        if two_factor["OTP_Validation_Required"] is True:
            mfa_url = urljoin(self.base_url, self.TWO_FACTOR_URL)
            uid = two_factor["unique_userID"]
            otp = self._totp.now()
            payload = {
                "uid": uid,
                "otp": otp
            }
            resp2 = requests.post(mfa_url, json=payload, verify=False)
            resp_data = resp2.json()
            token = resp2.json()["message_response"]["authentication"]["auth_data"]["auth_token"]
            return token

        return token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": self._auth_token}

# Basic full refresh stream
class DesktopCentralStream(HttpStream, ABC):
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class DesktopCentralStream(HttpStream, ABC)` which is the current class
    `class Customers(DesktopCentralStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(DesktopCentralStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalDesktopCentralStream((DesktopCentralStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """
    @property
    def envelope_name(self):
        return ""

    @property
    def url_base(self):
        return self.config["base_url"]

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    @property
    def max_retries(self) -> Union[int, None]:
        """
        Override if needed. Specifies maximum amount of retries for backoff policy. Return None for no limit.
        """
        return 100

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return 160

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
        envelope = response.json()["message_response"]

        check1 = "total" in envelope.keys()
        check2 = "limit" in envelope.keys()
        check3 = "page" in envelope.keys()
        
        if (check1 and check2) and check3:
            return {
                "total": envelope["total"],
                "limit": envelope["limit"],
                "page": envelope["page"]
            }

        return None

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        Override to return a mapping of keyword arguments to be used when creating the HTTP request.
        Any option listed in https://docs.python-requests.org/en/latest/api/#requests.adapters.BaseAdapter.send for can be returned from
        this method. Note that these options do not conflict with request-level options such as headers, request params, etc..
        """

        # NOTE: SSL Cert Verification disabled because the source has a self-signed certificate
        return {"verify": False}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            # NOTE: Handles the case where there's only one page of data
            total = int(next_page_token["total"])
            limit = int(next_page_token["limit"])
            page = int(next_page_token["page"])
            if total < limit:
                return {}
            else:
                # check how many records we've already collected
                already_collected = limit * page
                # and if we're still under the total keep goign
                if already_collected < total:
                    next_page = page + 1
                    return {"page": next_page, "pagelimit": limit}
                else:
                    return {}
        else:
            return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield from response.json()["message_response"][self.envelope_name]


class Computers(DesktopCentralStream):
    primary_key = "resource_id"
    envelope_name = "computers"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.3/som/computers"

class ScanComputers(DesktopCentralStream):
    primary_key = "resource_id"
    envelope_name = "scancomputers"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/scancomputers"

class Summary(DesktopCentralStream):
    # NOTE: This endpoint does not actually have a primary key it's just a summary
    #       of stats, and not a list of resources
    primary_key = "na"
    envelope_name = "summary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/som/summary"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

class AllSummary(DesktopCentralStream):
    primary_key = "na"
    envelope_name = "allsummary"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/inventory/allsummary"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        summary = response.json()["message_response"][self.envelope_name]
        yield from [summary]

class RemoteOffice(DesktopCentralStream):
    primary_key = "resource_id"
    envelope_name = "remoteoffice"
    
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "api/1.4/som/remoteoffice"

# Source
class SourceDesktopCentral(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            username = config["username"]
            password = config["password"]
            key = config["otp_key"]
            base_url = config["base_url"]
        except KeyError:
            return False, "Username / Password / OTP_key missing from config file, please check and try again."
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = OTPAuthenticator(
            username=config["username"],
            password=config["password"],
            otp_key=config["otp_key"],
            base_url=config["base_url"]
        )
        return [
            AllSummary(authenticator=auth, config=config),
            Computers(authenticator=auth, config=config),
            Summary(authenticator=auth, config=config),
            RemoteOffice(authenticator=auth, config=config),
        ]
