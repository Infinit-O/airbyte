from typing import Mapping, Any

from .base import WorkplaceByMetaStream
from .field_mixins import MemberFieldsMixin, GroupFieldsMixin

class CommunityAdmins(WorkplaceByMetaStream, MemberFieldsMixin):
    """
    Corresponds to the /community/admins endpoint.
    """
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/admins/"

class CommunityGroups(WorkplaceByMetaStream, GroupFieldsMixin):
    """
    Corresponds to the /community/groups endpoint. Not sure if it conflicts with / works with the
    /groups endpoint, hence the naming "CommunityGroups" to differentiate from just "Groups"
    """
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/groups/"

class CommunityMembers(WorkplaceByMetaStream, MemberFieldsMixin):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/members/"


class CommunityEvents(WorkplaceByMetaStream):
    primary_key = "id"
    # NOTE: Do NOT pass "location" in the fields for this stream because its reported as
    #       deprecated and will cause an error. 
    fields = [
        "description",
        "end_time",
        "name",
        "start_time",
    ]

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/events/"

class CommunityBadges(WorkplaceByMetaStream):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/badges/"

class CommunityKnowledgeLibraryCategories(WorkplaceByMetaStream):
    primary_key = "id"
    fields = []

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/knowledge_library_categories/"

class CommunityKnowledgeQuickLinks(WorkplaceByMetaStream):
    primary_key = "id"
    # NOTE: Do NOT pass "location" in the fields for this stream because its reported as
    #       deprecated and will cause an error. 
    fields = []

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/knowledge_quick_links/"

class CommunityFormerMembers(WorkplaceByMetaStream, MemberFieldsMixin):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/former_members/"
