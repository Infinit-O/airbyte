from abc import ABC
from typing import Any, Iterable, MutableMapping, Mapping, Tuple
from copy import deepcopy

import requests
import arrow
from .full_refresh_streams import SnipeitStream

from airbyte_cdk.sources.streams import IncrementalMixin

class Events(SnipeitStream, IncrementalMixin):
    primary_key = "id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value

    @property
    def cursor_field(self):
        return "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # NOTE: This was originally the key function in the max() call below
        #       I moved it out here to keep mypy happy.
        def __key_function(item: Tuple) -> Any:
            return item[1]
        if current_stream_state == {}:
            self.state = latest_record[self.cursor_field]
            return {self.cursor_field: latest_record[self.cursor_field]}
        else:
            records = {}
            records[current_stream_state[self.cursor_field]] = arrow.get(current_stream_state[self.cursor_field])
            records[latest_record[self.cursor_field]] = arrow.get(latest_record[self.cursor_field])
            # NOTE: mypy complains about records.items() not having the right type for max() but it works just fine
            #       in runtime regardless.
            latest_record = max(records.items(), key=__key_function)[0]   # type: ignore[arg-type]
            self.state[self.cursor_field] = latest_record
            return {self.cursor_field: latest_record}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "reports/activity/"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] , **kwargs) -> Iterable[Mapping]:
        """
        Parses response and returns a result set suitable for incremental sync. It takes in the stream state saved
        by Airbyte, and uses it to filter out records that have already been synced, leaving only the newest records.

        :return an iterable containing each record in the response
        """
        def __move_cursor_up(record: Mapping[str, Any]) -> Mapping[str, Any]:
            result: dict = deepcopy(record)
            result["updated_at"] = result["updated_at"]["datetime"]
            return result

        def _newer_than_latest(latest_record_date: arrow.Arrow, record: Mapping[str, Any]) -> bool:
            current_record_date = arrow.get(record["updated_at"])
            if current_record_date > latest_record_date:
                return True
            else:
                return False

        base = response.json().get("rows", [])
        self.total = response.json().get("total")
        # NOTE: Airbyte's recommendation is to transform the object so that the cursor is
        #       top-level.
        transformed = [__move_cursor_up(record) for record in base]

        if stream_state != {}:
            latest_record_date: arrow.Arrow = arrow.get(stream_state[self.cursor_field])
            if _newer_than_latest(latest_record_date, transformed[0]) == False:
                self.stop_immediately = True
                yield from []
            else:
                # NOTE: There's probably a more succint way of doing this but I can't think of it right now.
                ascending_list = reversed(transformed)
                only_the_newest: list = [x for x in ascending_list if _newer_than_latest(latest_record_date, x)]
                yield from only_the_newest
        else:
            ascending_list = reversed(transformed)
            yield from ascending_list

        # if self.state:
        #     latest_record_date = arrow.get(self.state.get(self.cursor_field))
        #     if _newer_than_latest(latest_record_date, transformed[0]) == False:
        #         self.stop_immediately = True
        #         yield from []
        #     else:
        #         ascending = reversed(transformed)
        #         only_the_newest = [x for x in ascending if _newer_than_latest(latest_record_date, x)]
        #         self.state = only_the_newest[0][self.cursor_field]
        #         yield from only_the_newest
        # else:
        #     ascending = reversed(transformed)
        #     self.state = transformed[0][self.cursor_field]
        #     yield from ascending
