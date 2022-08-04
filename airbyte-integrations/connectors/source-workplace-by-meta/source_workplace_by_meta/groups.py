from typing import Any, List, Mapping, Iterable
import requests

from .base import WorkplaceByMetaStream, WorkplaceByMetaSubstream
from .field_mixins import (
    GroupFieldsMixin,
    MemberFieldsMixin,
    EventFieldsMixin,
    GroupMemberFieldsMixin,
)

class Groups(WorkplaceByMetaStream, GroupFieldsMixin):
    """
    Corresponds to the /community/groups endpoint. Not sure if it conflicts with / works with the
    /groups endpoint, hence the naming "CommunityGroups" to differentiate from just "Groups"
    """
    primary_key = "id"

    def path(
        self,
        *,
        stream_state,
        stream_slice,
        next_page_token,
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
    #       the mixin. Not sure where I want to go from here.
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
    
    def parse_response(self, response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]

class GroupAdmins(WorkplaceByMetaSubstream, MemberFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/admins"

# NOTE, those probably need to be captured too
#       https://developers.facebook.com/docs/graph-api/reference/album
class GroupAlbums(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/albums"
    fields = [
        "id",
        "backdated_time",
        "backdated_granularity",
        "can_upload",
        "count",
        "cover_photo",
        "created_time",
        "description",
        "event",
        "from",
        "link",
        "location",
        "name",
        "place",
        "privacy",
        "type",
        "updated_time",
    ]

class GroupAutoMembershipRules(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/auto_membership_rules"
    fields = []

class GroupDocs(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/docs"
    fields = [
        "id",
        "can_delete",
        "can_edit",
        "created_time",
        "embedded_urls",
        "from",
        "icon",
        "link",
        "message",
        "revision",
        "subject",
        "updated_time",
    ]

class GroupEvents(WorkplaceByMetaSubstream, EventFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/events"

class GroupFeed(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/feed"
    fields = [
        "id",
        "created_time",
        "formatting",
        "from",
        "icon",
        "link",
        "message",
        "name",
        "object_id",
        "permalink_url",
        "picture",
        "place",
        "poll",
        "properties",
        "status_type",
        "story",
        "to",
        "updated_time",
        "with_tags"
    ]

class GroupFiles(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/files"
    fields = [
        "download_link",
        "from",
        "group",
        "id",
        "message",
        "updated_time",
    ]

class GroupMemberRequests(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/member_requests"
    fields = [
    ]

# NOTE: It's worth noting here that the fields exposed by this
#       edge are a subset of the fields used by other edges 
#       exposing user data, PLUS a few additional ones unique to this
#       edge. They're not exactly the same and to me it's not worth
#       factoring them out into their own hierarchy of mixins.
class GroupMembers(WorkplaceByMetaSubstream, GroupMemberFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/members"

# NOTE: This stream has a high chance of throwing an error once we're live.
class GroupModerators(WorkplaceByMetaSubstream, GroupMemberFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/moderators"

class GroupPinnedPosts(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = Groups
    path_template = "{entity_id}/pinned_posts"
    fields = []

