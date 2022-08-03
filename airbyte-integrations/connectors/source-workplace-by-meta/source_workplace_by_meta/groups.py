from typing import Any, List, Mapping, Iterable
import requests

from .base import WorkplaceByMetaStream, WorkplaceByMetaSubstream
from .field_mixins import GroupFieldsMixin, MemberFieldsMixin

class Groups(WorkplaceByMetaStream, GroupFieldsMixin):
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
        return "group/groups/"

class IndividualGroup(WorkplaceByMetaSubstream):
    primary_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/"
    foreign_key = "id"
    # NOTE: Individual Group endpoint doesn't quite use all the fields from
    #       the mixin.
    fields = [
        "id",
        "cover",
        "description",
        "icon",
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
        "is_official_group",
    ]
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]

class GroupAdmins(WorkplaceByMetaSubstream, MemberFieldsMixin):
    primary_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/admins"
    foreign_key = "id"
