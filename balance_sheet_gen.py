#!/usr/bin/env python3

import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor

from institutions import *
from institutions.institution import Institution as Institution


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="The path to a configuration file for this program",
    )
    args = parser.parse_args()

    logger = logging.getLogger("balance_sheet_gen")
    logging.basicConfig()

    column_balances = dict()

    with open(args.config, "r") as f:
        config = json.load(f)

    # init each column's class and retrieve the accounts' balance
    futures = dict()

    with ThreadPoolExecutor(max_workers=8) as executor:
        for column in config.get("columns", list()):
            try:
                column_institution = Institution(
                    type_name=column["type"],
                    name=column["name"],
                    config=column,
                    logger=logger.getChild(column["name"]),
                )

            except BaseException as be:
                logger.error(
                    f"Exception initializing {column['type']} - {type(be).__name__}: {str(be)}"
                )
                continue

            futures[executor.submit(column_institution.get_balance)] = column["name"]

    for future, column_name in futures.items():
        try:
            column_balances[column_name] = future.result()
        except BaseException as be:
            logger.error(
                f"Exception getting balance for {column_name} - {type(be).__name__}: {str(be)}"
            )

    # TODO instead of simply printing it,
    # a class of "communicators" should be used to allow output to files,
    # networked services, or a combination therein.
    for column_name, balance in column_balances.items():
        print(f"{column_name}: {balance}")


if __name__ == "__main__":
    main()
