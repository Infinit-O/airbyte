from abc import abstractmethod
from typing import Any, Iterable, List, Mapping

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .base_substream import ZohoRecruitSubStream
from .streams import ModuleSettings, ModuleRecords

# NOTE: Important note about the AssociatedRecords stream - it is a list of
#       JSON objects that does not have a defined schema. The schema in the
#       schemas/ directory reflects that, and is completely empty.
class AssociatedRecords(ZohoRecruitSubStream):
    primary_key = "id"
    parent_stream = ModuleSettings
    other_parent_stream = ModuleRecords
    path_template = "{module_api_name}/{record_id}/associate"
    api_field_name = "api_name"
    envelope_name = "data"

    # NOTE: This one's a triple whammy - we need the module_api_name, the records
    #       for EACH module_api_name, and then the IDs from each of the records
    def stream_slices(self, **kwargs):
        ps = self.parent_stream(authenticator=self._session.auth)
        ps_records = [
            x
            for x in ps.read_records(sync_mode=SyncMode.full_refresh)
            if x[self.api_field_name].lower() not in self.bad_api_list
        ]

        ops = self.other_parent_stream(authenticator=self._session.auth)
        today = pendulum.today()
        api_record_mapping = {}
        for api in ps_records:
            name = api[self.api_field_name]
            actual_records = [
                x
                for x in ops.read_records(
                    stream_slice={"module_api_name": api[self.api_field_name]},
                    sync_mode=SyncMode.full_refresh
                )
                if pendulum.parse(x["Created_Time"]) > today
            ]
            api_record_mapping[name] = actual_records
        
        for mapping in api_record_mapping.items():
            for item in mapping[1]:
                yield {
                    'module_api_name': mapping[0],
                    'record_id': item["id"]
                }

    def path(self, stream_slice, **kwargs):
        streamslice = stream_slice or {}
        endpath = self.path_template.format(
            record_id=streamslice["record_id"],
            module_api_name=streamslice["module_api_name"]
        )
        return endpath

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        """
        :return an iterable containisng each record in the response
        """
        # NOTE: Workaround for the fact that Zoho APIs seem to return 204 no content
        #       in place of an empty JSON response. sigh.
        if response.status_code == 204:
            yield from []
        else:
            # NOTE: Adding the candidate_id because Zoho Recruit doesn't have any way
            #       to associate these records "externally".
            # NOTE: origin_url is for debugging purposes.
            contents = response.json().get(self.envelope_name, [])
            if contents:
                for item in contents:
                    item["candidate_id"] = stream_slice["record_id"]
                    item["origin_url"] = response.request.url
            yield from contents
