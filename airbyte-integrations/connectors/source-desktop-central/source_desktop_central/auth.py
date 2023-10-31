from typing import Any, Mapping 
from base64 import urlsafe_b64encode
from urllib.parse import urljoin
import logging

import requests
import pyotp
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

class OTPAuthenticator(HttpAuthenticator):
    def __init__(self, username=None, password=None, base_url=None, otp_key=None, *args, **kwargs):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.logger = logging.getLogger('airbyte')
        self.LOGIN_URL = "/api/1.4/desktop/authentication"
        self.TWO_FACTOR_URL = "/api/1.4/desktop/authentication/otpValidate"
        self._totp = pyotp.TOTP(otp_key)
        self._auth_token = self.login()

    def login(self):
        # NOTE: Auth with Desktop Central occurs in 2 steps
        #       First, pass username and b64encoded password to auth endpoint
        #       Second, validate with OTP if needed
        b64_password = str(urlsafe_b64encode(bytes(self.password, "utf-8")), "utf-8")
        request_body = {
            "username": self.username,
            "password": b64_password,
            "auth_type": "local_authentication"
        }
        target_url = urljoin(self.base_url, self.LOGIN_URL)
        resp = requests.post(target_url, json=request_body, verify=False)
        resp.raise_for_status()

        resp = resp.json()
        self.logger.info("resp: {}".format(resp))

        try:
            two_factor = resp["message_response"]["authentication"]["two_factor_data"]
        except KeyError:
            two_factor = resp["message_response"]["authentication"]["auth_data"]["auth_token"]

        if two_factor["OTP_Validation_Required"] is True:
            mfa_url = urljoin(self.base_url, self.TWO_FACTOR_URL)
            uid = two_factor["unique_userID"]
            otp = self._totp.now()
            payload = {
                "uid": uid,
                "otp": otp
            }
            resp2 = requests.post(mfa_url, json=payload, verify=False)
            resp_data = resp2.json()
            token = resp_data["message_response"]["authentication"]["auth_data"]["auth_token"]
            return token

        return token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": self._auth_token}
