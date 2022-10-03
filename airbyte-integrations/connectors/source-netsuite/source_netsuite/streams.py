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
