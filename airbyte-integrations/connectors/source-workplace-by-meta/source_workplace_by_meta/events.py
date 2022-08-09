from typing import Mapping, Any, Iterable

from .base import WorkplaceByMetaSubstream
from .field_mixins import EventFieldsMixin, MemberFieldsMixin
from .community import CommunityEvents

class IndividualEvent(WorkplaceByMetaSubstream, EventFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CommunityEvents
    path_template = "{entity_id}"
    fields = [
        "id",
        "attending_count",
        "cover",
        "declined_count",
        "description",
        "end_time",
        "event_times",
        "guest_list_enabled",
        "interested_count",
        "maybe_count",
        "name",
        "owner",
        "parent_group",
        "place",
        "updated_time",
    ]

    def parse_response(self, response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]

class EventAdmins(WorkplaceByMetaSubstream, MemberFieldsMixin):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CommunityEvents
    path_template = "{entity_id}/admins"

class EventPictures(WorkplaceByMetaSubstream):
    primary_key = "id"
    foreign_key = "id"
    parent_stream = CommunityEvents
    path_template = "{entity_id}/admins"
 