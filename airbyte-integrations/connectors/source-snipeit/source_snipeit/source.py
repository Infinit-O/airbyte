#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from urllib.parse import urljoin
from typing import Any, List, Mapping, Tuple

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    Accessories,
    Categories,
    Consumables,
    Companies,
    Components,
    Departments,
    Events,
    Hardware,
    Licenses,
    Locations,
    Models,
    Manufacturers,
    Maintenances,
    StatusLabels,
    Users,
)

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

# Source
class SourceSnipeit(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        err_message = None

        token = config.get("access_token", None)
        logger.debug(f"Token present? {bool(token)}")
        base_url = config.get("base_url", None)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        full_url = urljoin(base_url, "/api/v1/hardware")
        logger.debug(f"Sending a request to: {full_url}")
        z = requests.get(full_url, headers=headers)
        logger.debug(f"Status code of response: {z.status_code}")
        try:
            z.raise_for_status()
            ok = True
        except Exception as e:
            err_message = repr(e)

        return ok, err_message


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        access_jwt = config.get("access_token")
        auth = TokenAuthenticator(token=access_jwt) 
        return [
            Accessories(authenticator=auth, config=config),
            Categories(authenticator=auth, config=config),
            Companies(authenticator=auth, config=config),
            Components(authenticator=auth, config=config),
            Consumables(authenticator=auth, config=config),
            Departments(authenticator=auth, config=config),
            Events(authenticator=auth, config=config),
            Hardware(authenticator=auth, config=config),
            Licenses(authenticator=auth, config=config),
            Locations(authenticator=auth, config=config),
            Maintenances(authenticator=auth, config=config),
            Manufacturers(authenticator=auth, config=config),
            Models(authenticator=auth, config=config),
            StatusLabels(authenticator=auth, config=config),
            Users(authenticator=auth, config=config),
        ]
