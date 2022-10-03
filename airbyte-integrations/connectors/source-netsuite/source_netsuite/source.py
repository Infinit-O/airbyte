#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .custom_authenticator import NetsuiteOauth2Authenticator
from .streams import (
    CreditMemo,
    CreditMemoList
)

# Basic full refresh stream
# class Customers(NetsuiteStream):
#     primary_key = "customer_id"

#     def path(
#         self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
#     ) -> str:
#         """
#         Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
#         should return "customers". Required.
#         """
#         return "customers"

# Source
class SourceNetsuite(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        cant_be_empty = ["account_id", "client_id", "certificate_id"]
        for x in cant_be_empty:
            if config[x] == "":
                self.logger.debug(f"{x} is empty string. Check config and try again.")
                return False, f"{x} cannot be empty string!"
        logger.info("Config file passes.")

        logger.info("Checking to see if private key is valid.")
        try:
            auth = NetsuiteOauth2Authenticator(
                config["client_id"],
                config["certificate_id"],
                config["private_key"],
                config["account_id"],
            )
            header = auth.get_auth_header()
            logger.debug(f"Header: {header}")
            assert header
        except Exception as e:
            raise Exception(f"Error: {e}") from e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = NetsuiteOauth2Authenticator(
            config["client_id"],
            config["certificate_id"],
            config["private_key"],
            config["account_id"]
        )
        return [
            CreditMemo(authenticator=auth, config=config),
            CreditMemoList(authenticator=auth, config=config)
        ]
