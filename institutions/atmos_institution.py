import logging
from time import sleep
from typing import Dict

import pyotp
import requests

from .institution import Institution


class AtmosInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)
        self.name = name
        self.config = config

        self.API_ROOT = "https://api.joinatmos.com/v1"

        self.api_session = requests.Session()
        self.api_session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0"
        self.api_session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }
        self.login()

    def login(self):
        login_json = {
            "email": self.config["email"],
            "password": self.config["password"],
        }

        login_res = self.api_session.post(
            f"{self.API_ROOT}/users/auth", json=login_json
        ).json()

        self.api_session.headers["Authorization"] = f"Bearer {login_res['token']}"

        # do MFA if prompted
        if login_res["tfa_setup"]:
            otp = pyotp.TOTP(self.config["totp_secret"])
            totp_code = otp.now()
            mfa_json = {"otp": totp_code}
            mfa_res = self.api_session.post(
                f"{self.API_ROOT}/users/auth/challenge", json=mfa_json
            ).json()

            # TODO double-check the bearer thing
            self.api_session.headers[
                "Authorization"
            ] = f"Bearer bearer {mfa_res['token']}"

    def get_balance(self) -> float:
        accounts = self.api_session.get(f"{self.API_ROOT}/account/nodes").json()[
            "nodes"
        ]
        for account in accounts:
            if account["info"]["nickname"] == self.config["account_name"]:
                return account["info"]["balance"]["amount"]

        raise Exception(
            f"Account with nickname '{self.config['account_name']}' not found"
        )
