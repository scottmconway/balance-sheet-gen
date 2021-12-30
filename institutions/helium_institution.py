import logging
from typing import Dict

import requests

from .institution import Institution


class HeliumInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)
        self.name = name
        self.config = config

        self.HELIUM_API_URL = "https://api.helium.io"

        self.current_exchange_rate = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "helium", "vs_currencies": "usd"},
        ).json()["helium"]["usd"]

    def get_balance(self) -> int:
        total = 0
        for wallet_addr in self.config.get("wallet_addrs", list()):
            res = requests.get(
                f"{self.HELIUM_API_URL}/v1/accounts/{wallet_addr}"
            ).json()

            # for some reason, I guess we use 10**8 representation of HNT?
            total += (res["data"]["balance"] * 10 ** -8) * self.current_exchange_rate

        return round(total)
