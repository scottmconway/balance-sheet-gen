import logging
from typing import Dict

import requests

from .institution import Institution


class EthereumInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)
        self.name = name
        self.config = config

        self.ADDRESS_BALANCE_URL = "https://ethplorer.io/service/service.php"
        self.current_exchange_rate = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "ethereum", "vs_currencies": "usd"},
        ).json()["ethereum"]["usd"]

    def get_balance(self) -> float:
        total = 0
        for wallet_addr in self.config.get("wallet_addrs", list()):
            res = requests.get(
                self.ADDRESS_BALANCE_URL, params={"data": wallet_addr}
            ).json()
            total += res["balance"] * self.current_exchange_rate

        return round(total, 2)
