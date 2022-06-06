import logging
import time
from typing import Dict

import cbpro
from pycoingecko import CoinGeckoAPI

from .institution import Institution


class CoinbaseProInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)

        self.COIN_NAME_REPLACEMENTS = {
            "avalanche": "avalanche-2",
            "ether": "ethereum",
            "polygon": "matic-network",
        }

        self.cb_pro_client = cbpro.AuthenticatedClient(
            config["api_key"], config["api_secret"], config["passphrase"]
        )
        self.coin_gecko = CoinGeckoAPI()

    def get_balance(self) -> float:
        total = 0

        # Get ready to convert tickers to names,
        # so we can ask coingecko for the price
        ticker_lookup = dict()
        currencies = self.cb_pro_client.get_currencies()
        for currency in currencies:
            ticker_lookup[currency["id"]] = currency["name"].lower().replace(" ", "-")

        accounts = self.cb_pro_client.get_accounts()
        for acct in accounts:
            # note that we could also use the "available" field if we wanted to

            # eveything (except bools?) is a string!
            balance = float(acct["balance"])
            if balance > 0:
                # acct has the coin's ticker, and coingecko wants the name
                # eg BTC -> bitcoin
                # TODO could operate on all coin IDs instead of one at a time

                coin_name = ticker_lookup[acct["currency"]]

                # See if we have a hard-coded re-name for this currency
                # by default, stick to the current name
                coin_name = self.COIN_NAME_REPLACEMENTS.get(coin_name, coin_name)

                # here's to hoping there aren't any other odd cases like this
                if coin_name == "united-states-dollar":
                    usd_rate = 1
                else:
                    usd_rate = self.coin_gecko.get_price(coin_name, "usd")[coin_name][
                        "usd"
                    ]

                total += balance * usd_rate

                time.sleep(1)  # Let's not hit CG's rate limit

        return round(total, 2)
