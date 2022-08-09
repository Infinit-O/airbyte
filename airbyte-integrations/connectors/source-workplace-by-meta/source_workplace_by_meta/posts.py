from typing import Mapping, Any

from .base import WorkplaceByMetaStream, WorkplaceByMetaSubstream
from .groups import GroupFeed
from .field_mixins import MemberFieldsMixin, GroupFieldsMixin, EventFieldsMixin, PostFieldsMixin

# NOTE: I've decided to assign GroupFeed as the parent of the
#       entire set of Posts streams, because it seems like the most
#       complete and comprehensive.
# class IndividualPost(WorkplaceByMetaSubstream, PostFieldsMixin):
#     primary_key = "id"
#     foreign_key = "id"
#     parent_stream = GroupFeed
#     path_template = "{entity_id}"


