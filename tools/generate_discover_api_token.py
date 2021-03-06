#!/usr/bin/env python3

import argparse
import base64
import getpass
import logging
import secrets
import sys

import requests
from requests.exceptions import HTTPError

DISCOVER_MAPI_BASE = "https://mapi.discover.com"

# TODO source this value from the version listed on the play store
APP_VERSION = "2112.0"

QUICKVIEW_URL = "https://mapi.discovercard.com/cardsvcs/acs/quickview/v4/view"

logger = logging.getLogger("generate_discover_api_token")
logging.basicConfig()
logger.setLevel(logging.INFO)


def make_device_token() -> str:
    """
    Returns a "device token" compatible string,
    defined as 64 random bytes expressed as a base64 string

    This also checks the rare case that it collides with a device token
    that's already registered on Discover's side!
    :return: A randomized API token for Discover's mobile API,
        guaranteed to not overlap with a token that's being used.
    :rtype: str
    """

    # note that this will run as long as the API returns HTTP-200 status codes

    while True:
        device_token = base64.b64encode(secrets.token_bytes(64)).decode()

        res = get_quick_view_res(device_token)
        if res.status_code != 200 or res.json()["bankDetails"] is None:
            return device_token


def get_quick_view_res(device_token: str):
    """
    :param device_token: A valid mobile API token
    :type device_token: str
    :return: A quick view response object
    :rtype: requests.model.Response
    """

    # These headers taken from a call made by Discover's Android app
    headers = {
        "User-Agent": "okhttp/3.12.12",
        "X-Client-Platform": "Android",
        "X-Application-Version": APP_VERSION,
        "Adrum_1": "isMobile:true",
        "Adrum": "isAjax:true",
    }

    quick_view_json = {
        "cardDeviceToken": None,
        "bankDeviceToken": device_token,
        "getCardImage": True,
    }

    return requests.post(QUICKVIEW_URL, headers=headers, json=quick_view_json)


def check_token(token: str) -> None:
    """
    Given a (hopefully) valid token, print out all accounts tied to it

    :param token: A device ID token, possibly generated by make_device_token()
    :type token: str
    :rtype: None
    """

    try:
        res = get_quick_view_res(token)
        res.raise_for_status()
        quick_view = res.json()
    except BaseException as be:
        logger.error(f"Error checking token - {be}")
        sys.exit(1)

    for k, v in quick_view.items():
        if k.startswith("error") and v:
            logger.error(f"Error checking token in discover response - {k}")
            sys.exit(1)

    for acct in quick_view["bankDetails"]["bankAccount"]:
        logger.info(
            f"ID: {acct['id']}, "
            f"nickname: {acct['nickName']}, "
            f"balance: {acct['balance']['formatted']}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        help="Valid modes: generate_token, delete_token, check_token - "
        "defaults to generate_token",
        default="generate_token",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="The email address of your DiscoverBank account",
        default=None,
    )
    args = parser.parse_args()
    if args.mode not in ["generate_token", "delete_token", "check_token"]:
        logger.error(f'Invalid mode "{args.mode}". Exiting')
        sys.exit(1)

    if args.mode == "check_token":
        token = input("Enter your API token: ")
        check_token(token)

    # else, login (needed for binding and unbinding)
    else:
        user_id = args.username if args.username else input("Enter username: ")
        password = getpass.getpass("Enter password: ")

        login_headers = {
            "X-Client-Platform": "Android",
            "X-Application-Version": APP_VERSION,
            "X-Did": "a",
            "X-Sid": None,
            "X-Oid": "a",
            "X-Screen-Name": "CORE_LOGIN_SCREEN",
            "X-Build-Variant": "FIDO",
            "Accept": "application/json",
            "X-Sec-Token": None,
            "User-Agent": f"DiscoverFinancialMobile/{APP_VERSION} (android;25)",
            "X-Acf-Sensor-Data": "a",
            "Adrum_1": "isMobile:true",
            "Adrum": "isAjax:true",
        }

        login_json = {
            "username": user_id,
            "password": password,
            "loginTab": "UNIVERSAL",
        }

        login_res = requests.post(
            DISCOVER_MAPI_BASE + "/portal", headers=login_headers, json=login_json
        )

        try:
            login_res.raise_for_status()

        except HTTPError as he:
            logger.error(f"Error logging in - {he} - exiting")
            sys.exit(1)

        api_links = login_res.json()["_links"]
        quickview_binding = api_links["quickview:bind"]["href"]

        auth_header = "Bearer " + login_res.headers["X-Session-Token"]

        # This is for naught if the operation is deletion,
        # but make a device token anyway
        device_token = make_device_token()

        bind_headers = {
            "Host": "mapi.discoverbank.com",
            "X-Client-Platform": "Android",
            "X-Application-Version": "2112.0",
            "X-Device-Id": device_token,
            "Content-Type": "application/json",
            "Authorization": auth_header,
            "User-Agent": "DiscoverFinancialMobile/2112.0 (android;25)",
            "Content-Length": "0",
        }

        if args.mode == "delete_token":
            bind_headers["X-Http-Method-Override"] = "DELETE"
            bind_headers["X-Device-Id"] = input("Enter the API key to be unbound: ")

        # This call binds the device token to the account
        bind_res = requests.post(quickview_binding, headers=bind_headers)

        try:
            bind_res.raise_for_status()
        except HTTPError:
            logger.error("Unable to make API binding - exiting")
            sys.exit(1)

        if args.mode == "generate_token":
            logger.info(
                'Generated API token: "%s"\n'
                "You should recieve an email from Discover "
                "confirming this action shortly" % device_token
            )

            check_token(device_token)

        # args.mode == delete_token
        else:
            logger.info("Successfully unbound token")


if __name__ == "__main__":
    main()
