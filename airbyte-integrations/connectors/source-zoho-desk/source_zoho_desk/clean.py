from typing import Mapping, Any, MutableMapping
from .base import ZohoDeskStream, ZohoDeskIncrementalStream, ZohoDeskSubstream

class Agents(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "agents"

class Roles(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "roles"

class Departments(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "departments"

class Tickets(ZohoDeskIncrementalStream):
    primary_key = "id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit = 100

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return {"limit": self.limit, "from": next_page_token["from"], "sortBy": "-createdTime"}
        else:
            return {"limit": self.limit, "sortBy": "-createdTime"}

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "tickets"
    
class ArchivedTickets(ZohoDeskSubstream):
    parent = Tickets
    primary_key = "id"

    def request_params(self, 
                       stream_state: Mapping[str, Any], 
                       stream_slice: Mapping[str, Any] = None,
                       next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if stream_slice:
            return {
                "departmentId": stream_slice["department_id"]
            }
        else:
            return {}
        
    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "tickets/archivedTickets"

class Contacts(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "contacts"

class Accounts(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "accounts"

class Tasks(ZohoDeskStream):
    primary_key = "id"
    
    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "tasks"

class RecycleBin(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "recycleBin"

class Users(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "users"

class BusinessHours(ZohoDeskStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "businessHours"
