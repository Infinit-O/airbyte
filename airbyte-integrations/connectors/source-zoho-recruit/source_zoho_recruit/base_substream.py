from abc import abstractmethod

from airbyte_cdk.models import SyncMode
from .base import ZohoRecruitStream

class ZohoRecruitSubStream(ZohoRecruitStream):
    @property
    @abstractmethod
    def path_template(self):
        pass

    @property
    @abstractmethod
    def parent_stream(self):
        pass

    @property
    @abstractmethod
    def api_field_name(self):
        pass

    @property
    def bad_api_list(self):
        unauthorized_api_list = ["referrals"]
        unsupported_api_list = ["home", "analytics", "emails", "documents", "social", "zoho_marketplace"]
        invalid_name_list = ["reports", "dashboards", "metrics",] 
        empty_api_list = ["approvals"]
        bad_list = unsupported_api_list + empty_api_list + unauthorized_api_list + invalid_name_list
        return bad_list
    
    @property
    def envelope_name(self):
        pass

    def stream_slices(self, **kwargs):
        items = self.parent_stream(authenticator=self._session.auth)
        for item in items.read_records(sync_mode=SyncMode.full_refresh):
            # NOTE: Zoho API throws an error when you try to get the module details
            #       for the "home" module
            #       apparently, it doesn't support a call to details
            if self.bad_api_list and item["api_name"].lower() in self.bad_api_list:
                continue
            else:
                yield {"module_api_name": item[self.api_field_name]}

    def path(self, stream_slice, **kwargs):
        streamslice = stream_slice or {}
        return self.path_template.format(module_api_name=streamslice["module_api_name"])
