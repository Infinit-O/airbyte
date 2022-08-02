from typing import Mapping, Any

from .base import WorkplaceByMetaStream

class Admins(WorkplaceByMetaStream):
    """
    Corresponds to the /community/admins endpoint.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"
    fields = [
        "id", "first_name", "last_name", "email", "title",
        "organization", "division", "department", "primary_phone",
        "primary_address", "picture", "link", "locale", "name",
        "name_format", "updated_time", "account_invite_time",
        "account_claim_time", "external_id", "start_date", "about",
        "cost_center", "claim_link", "access_code", "work_locale",
        # "frontline",
        "active"
    ]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/admins/"

class CommunityGroups(WorkplaceByMetaStream):
    """
    Corresponds to the /community/groups endpoint. Not sure if it conflicts with / works with the
    /groups endpoint, hence the naming "CommunityGroups" to differentiate from just "Groups"
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"
    fields = [
        "id",
        "cover",
        "cover_url",
        "description",
        "icon",
        "is_workspace_defalt",
        "is_community",
        "name",
        "owner",
        "privacy",
        "updated_time",
        "archived",
        "post_requires_admin_approval",
        "purpose",
        "post_permissions",
        "join_setting",
        "sorting_setting",
        "is_official_group",
    ]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "community/groups/"
