import logging
from time import sleep
from typing import Dict

import requests

from .institution import Institution


def err_check(res: requests.models.Response) -> None:
    """
    Simple function to check API responses for errors

    :param res: A response from Discover's mobile API via requests
    :type res: requests.models.Response
    :rtype: None
    """

    res.raise_for_status()
    js = res.json()

    # This API returns errors _under different field names, mind you_
    # with 2XX status codes
    #
    # Thanks Discover!

    # errorRetrievingBankData seems to be raised if we send two requests
    # less then a few seconds apart
    for err in ["errorRetrievingBankData", "errorRetrievingCardData"]:
        if js.get(err, False):
            raise Exception(f"Error in JSON response - {err}, {js}")


class DiscoverBankInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)
        self.name = name
        self.config = config

        self.QUICK_VIEW_URL = (
            "https://mapi.discovercard.com/cardsvcs/acs/quickview/v4/view"
        )

        self.api_session = requests.Session()
        self.api_session.hooks = {"response": lambda r, *args, **kwargs: err_check(r)}

        self.APP_VERSION = "2112.0"
        self.MAX_RETRIES = 5

    def get_balance(self) -> float:
        headers = {
            "Host": "mapi.discovercard.com",
            "X-Client-Platform": "Android",
            "X-Application-Version": self.APP_VERSION,
            "X-Screen-Name": "CORE_LOGIN_SCREEN",
            "X-Build-Variant": "DEFAULT_BUILD",
            "Accept": "application/json",
            "X-Sec-Token": "",
            "User-Agent": f"DiscoverFinancialMobile/{self.APP_VERSION} (android;25)",
            "Adrum_1": "isMobile:true",
            "Adrum": "isAjax:true",
        }

        data = {
            "bankDeviceToken": self.config["api_key"],
            "cardDeviceToken": None,
            "getCardImage": True,
        }

        account_not_found = False
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                res = self.api_session.post(
                    self.QUICK_VIEW_URL, json=data, headers=headers
                )
                for acct in res.json()["bankDetails"]["bankAccount"]:
                    if acct["id"] == self.config["account_id"]:
                        return round(float(acct["availableBalance"]["value"]), 2)

                account_not_found = True
                break

            except BaseException as be:
                last_exception = be
                sleep(5)
                continue

        # Raise any exception after we hit the retry timer
        if account_not_found:
            raise Exception(f'Account of id "{self.config["account_id"]}" not found')
        elif last_exception:
            raise last_exception
