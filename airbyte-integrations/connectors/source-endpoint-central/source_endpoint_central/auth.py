from typing import Any, Mapping 
import logging

import requests

from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

class OTPAuthenticator(HttpAuthenticator):
    def __init__(self, apikey=None, base_url=None, *args, **kwargs):
        self.apikey = apikey
        self.base_url = base_url

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": self.apikey}
    @property
    def verify_ssl(self):
        return False
