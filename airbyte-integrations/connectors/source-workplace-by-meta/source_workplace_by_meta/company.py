from typing import Any, Iterable, Mapping, MutableMapping

from .base import WorkplaceByMetaStream, WorkplaceByMetaSubstream
from .field_mixins import (
    MemberFieldsMixin,
    GroupFieldsMixin,
    EventFieldsMixin,
    PostFieldsMixin,
)

class CompanyMembers(WorkplaceByMetaStream, MemberFieldsMixin):
    # NOTE: Returns all members of the company, MINUS the inactive ones.
    primary_key = "id"

    def path(
        self,
        *,
        stream_state,
        stream_slice,
        next_page_token,
    ) -> str:
        return "/company/members"

class CompanyInactiveMembers(WorkplaceByMetaStream, MemberFieldsMixin):
    primary_key = "id"

    def path(
        self,
        *,
        stream_state,
        stream_slice,
        next_page_token,
    ) -> str:
        return "/company/organization_members"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        state_above = super().request_params(stream_state, stream_slice, next_page_token)
        state_above["inactive"] = 1
        return state_above

# NOTE: The "member" streams will be kept here, as their parent is the CompanyMembers stream.
class MemberEvents(WorkplaceByMetaSubstream, EventFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/events"

class MemberFeed(WorkplaceByMetaSubstream, MemberFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/feed"

class MemberManagers(WorkplaceByMetaSubstream, MemberFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/managers"

# NOTE: The schema for this is ProfilePictureSource
#       in the FB graph API.
class MemberPhotos(WorkplaceByMetaSubstream):
    primary_key = "cache_key"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/photos"
    fields = [
        "cache_key",
        "height",
        "is_silhouette",
        "url",
        "width",
    ]

class MemberGroups(WorkplaceByMetaSubstream, GroupFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/groups"

# NOTE: There IS data, but there isn't a documentation page showing how
#       phone numbers are stored.
class MemberPhones(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/phones"
    fields = []

class MemberSkills(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/skills"
    fields = []

class MemberBadges(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}/badges"
    fields = []

class IndividualMember(WorkplaceByMetaSubstream, MemberFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CompanyMembers
    path_template = "{entity_id}"

    def parse_response(self, response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]

class ReportedContent(WorkplaceByMetaStream):
    primary_key = "id"
    fields = []

    def path(
        self,
        *,
        stream_state,
        stream_slice,
        next_page_token,
    ) -> str:
        return "/company/reported_content"
