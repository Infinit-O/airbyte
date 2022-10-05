from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from .base_stream import NetsuiteStream, NetsuiteChildStream


class CreditMemoList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "creditMemo"

class CreditMemo(NetsuiteChildStream):
    parent = CreditMemoList
    primary_key = "id"
    fk_name = "id"
    fk = "id"
    path_template = "creditmemo/{entity_id}"

class CustomerList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "customer"

class Customer(NetsuiteChildStream):
    parent = CustomerList
    primary_key = "id"
    fk_name = "id"
    fk = "id"
    path_template = "customer/{entity_id}"

class EmailTemplateList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "emailTemplate"

class EmailTemplate(NetsuiteChildStream):
    parent = EmailTemplateList
    primary_key = "id"
    fk_name = "id"
    fk = "id"
    path_template = "emailTemplate/{entity_id}"

class EmployeeList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "employee"

class Employee(NetsuiteChildStream):
    parent = EmployeeList
    primary_key = "id"
    fk_name = "employee_id"
    fk = "id"
    path_template = "employee/{entity_id}"

class InvoiceList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "invoice"

class Invoice(NetsuiteChildStream):
    parent = InvoiceList
    primary_key = "id"
    fk_name = "invoice_id"
    fk = "id"
    path_template = "invoice/{entity_id}"

class JournalEntryList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "journalEntry"

class JournalEntry(NetsuiteChildStream):
    parent = JournalEntryList 
    primary_key = "id"
    fk_name = "journal_entry_id"
    fk = "id"
    path_template = "journalEntry/{entity_id}"

class MessageList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "message"

class Message(NetsuiteChildStream):
    parent = MessageList
    primary_key = "id"
    fk_name = "message_id"
    fk = "id"
    path_template = "message/{entity_id}"

class PurchaseOrderList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "purchaseOrder"

class PurchaseOrder(NetsuiteChildStream):
    parent = PurchaseOrderList
    primary_key = "id"
    fk_name = "purchase_order_id"
    fk = "id"
    path_template = "purchaseOrder/{entity_id}"

class SubsidiaryList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "subsidiary"

class Subsidiary(NetsuiteChildStream):
    parent = SubsidiaryList
    primary_key = "id"
    fk_name = "subsidiary_id"
    fk = "id"
    path_template = "subsidiary/{entity_id}"

class VendorBillList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "vendorBill"
    
class VendorBill(NetsuiteChildStream):
    parent = VendorBillList 
    primary_key = "id"
    fk_name = "subsidiary_id"
    fk = "id"
    path_template = "vendorBill/{entity_id}"

class VendorList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "vendor"

class Vendor(NetsuiteChildStream):
    parent = VendorList
    primary_key = "id"
    fk_name = "vendor_id"
    fk = "id"
    path_template = "vendor/{entity_id}"

class VendorSubsidiaryRelationshipList(NetsuiteStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "vendorSubsidiaryRelationship"

class VendorSubsidiaryRelationship(NetsuiteChildStream):
    parent = VendorSubsidiaryRelationshipList
    primary_key = "id"
    fk_name = "vendor_id"
    fk = "id"
    path_template = "vendorSubsidiaryRelationship/{entity_id}"
