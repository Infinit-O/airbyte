#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .custom_authenticator import NetsuiteOauth2Authenticator
from .streams import (
    AssemblyItemList,
    AssemblyItem,
    CalendarEventList,
    CalendarEvent,
    ContactRoleList,
    ContactRole,
    CreditMemo,
    CreditMemoList,
    CustomerList,
    CustomerSubsidiaryRelationshipList,
    CustomerSubsidiaryRelationship,
    Customer,
    EmailTemplateList,
    EmailTemplate,
    EmployeeList,
    Employee,
    InvoiceList,
    Invoice,
    JournalEntryList,
    JournalEntry,
    MessageList,
    Message,
    PurchaseOrderList,
    PurchaseOrder,
    SubsidiaryList,
    Subsidiary,
    VendorBillList,
    VendorBill,
    VendorList,
    Vendor,
    VendorSubsidiaryRelationship,
    VendorSubsidiaryRelationshipList,
)

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
            AssemblyItemList(authenticator=auth, config=config),
            AssemblyItem(authenticator=auth, config=config),
            CalendarEventList(authenticator=auth, config=config),
            CalendarEvent(authenticator=auth, config=config),
            CreditMemo(authenticator=auth, config=config),
            CreditMemoList(authenticator=auth, config=config),
            ContactRoleList(authenticator=auth, config=config),
            ContactRole(authenticator=auth, config=config),
            CustomerList(authenticator=auth, config=config),
            CustomerSubsidiaryRelationshipList(authenticator=auth, config=config),
            CustomerSubsidiaryRelationship(authenticator=auth, config=config),
            Customer(authenticator=auth, config=config),
            EmployeeList(authenticator=auth, config=config),
            Employee(authenticator=auth, config=config),
            EmailTemplateList(authenticator=auth, config=config),
            EmailTemplate(authenticator=auth, config=config),
            InvoiceList(authenticator=auth, config=config),
            Invoice(authenticator=auth, config=config),
            MessageList(authenticator=auth, config=config),
            JournalEntryList(authenticator=auth, config=config),
            JournalEntry(authenticator=auth, config=config),
            Message(authenticator=auth, config=config),
            PurchaseOrderList(authenticator=auth, config=config),
            PurchaseOrder(authenticator=auth, config=config),
            SubsidiaryList(authenticator=auth, config=config),
            Subsidiary(authenticator=auth, config=config),
            VendorBillList(authenticator=auth, config=config),
            VendorBill(authenticator=auth, config=config),
            VendorList(authenticator=auth, config=config),
            Vendor(authenticator=auth, config=config),
            VendorSubsidiaryRelationshipList(authenticator=auth, config=config),
            VendorSubsidiaryRelationship(authenticator=auth, config=config),
        ]
