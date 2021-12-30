import logging
import time
from typing import Dict

from coinbase.wallet.client import Client

from .institution import Institution


class CoinbaseInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)

        self.coinbase_client = Client(config["api_key"], config["api_secret"])

    def get_balance(self) -> int:
        total = 0
        starting_after = None

        while True:  # Paginate until we hit the last page
            accounts = self.coinbase_client.get_accounts(
                limit=100, starting_after=starting_after
            )
            if accounts.pagination.next_starting_after is not None:
                starting_after = accounts.pagination.next_starting_after
                for acct in accounts.data:
                    total += float(acct.native_balance.amount)

                time.sleep(1)  # Let's not hit the rate limit
            else:
                for acct in accounts.data:
                    total += float(acct.native_balance.amount)
                break

        return round(total)
