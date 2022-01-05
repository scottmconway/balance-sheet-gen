import logging
from typing import Dict

import requests

from .institution import Institution


class ChiaInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)
        self.name = name
        self.config = config

        self.ADDRESS_BALANCE_URL = "https://xchscan.com/api/account/balance"

        self.current_exchange_rate = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "chia", "vs_currencies": "usd"},
        ).json()["chia"]["usd"]

    def get_balance(self) -> float:
        total = 0
        for wallet_addr in self.config["wallet_addrs"]:

            res = requests.get(
                self.ADDRESS_BALANCE_URL, params={"address": wallet_addr}
            ).json()
            total += res["xch"]

        return round(total * self.current_exchange_rate, 2)
