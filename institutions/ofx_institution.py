import datetime
import logging
import xml.etree.ElementTree as ET
from typing import Dict

import ofxtools
from ofxtools.Client import InvStmtRq


from .institution import Institution


class OfxInstitution(Institution):
    def __init__(self, type_name: str, name: str, config: Dict, logger: logging.Logger):
        super(type(self), self).__init__(type_name, name, config, logger)
        self.name = name
        self.config = config
        # assert some time in the past
        self.dtstart = datetime.datetime(1990, 1, 1, tzinfo=ofxtools.utils.UTC)
        # assert some time in the future
        self.dtend = datetime.datetime(
            datetime.date.today().year + 1, 1, 1, tzinfo=ofxtools.utils.UTC
        )

        # init OFX client, but don't auth
        #
        # this means validating the user's config
        # well, except for connecting via OFX

        # expected config values:
        """
        "username": "",
        "password": "",
        "account_id": "",
        "account_type": "",
        institution_info: {
            "org": "",
            "broker_id": "",
            "bank_id": "",
            "fid": "",
            "url": ""

            OR

            "ofxget_freindly_name": ""
            ""
        }
        """

        # These params are what ofxtools used, so I'm going with them
        self.DEFAULT_CLIENT_UID = "0A7590EE-2818-4A60-9CAA-16F9EC41E043"
        self.DEFAULT_APP_ID = "QWIN"
        self.DEFAULT_APP_VERSION = "2700"
        self.DEFAULT_LANG = "ENG"
        self.DEFAULT_VERSION = 220

        # TODO if "ofxget_friendly_name", derive necessary attrs

        # init client
        self.client = ofxtools.OFXClient(
            self.config["institution_info"]["url"],
            userid=self.config["username"],
            org=self.config["institution_info"]["org"],
            fid=self.config["institution_info"]["fid"],
            version=self.DEFAULT_VERSION,
            appid=self.DEFAULT_APP_ID,
            appver=self.DEFAULT_APP_VERSION,
            language=self.DEFAULT_LANG,
            prettyprint=False,
            close_elements=True,
            bankid=self.config["institution_info"].get("bankid", None),
            brokerid=self.config["institution_info"]["broker_id"],
            clientuid=self.DEFAULT_CLIENT_UID,
        )

    def get_balance(self) -> float:
        # if self.config['account_type'] == 'investment':
        # elif self.config['account_type'] == 'credit':

        # TODO assuming this is indeed an investment account
        stmt_req = InvStmtRq(
            acctid=self.config["account_id"],
            dtstart=self.dtstart,
            dtend=self.dtend,
            dtasof=None,
            inctran=True,
            incoo=False,
            incpos=True,
            incbal=True,
        )

        stmt_res = self.client.request_statements(
            self.config["password"], stmt_req, dryrun=False, gen_newfileuid=False
        )
        tree = ET.parse(stmt_res)
        acct_balance = 0

        # TODO do we need to check for account types besides "investment"?
        # if self.config['account_type'] == 'investment':

        # TODO is this valid for all types of investment accounts?
        balances = tree.findall(
            "./INVSTMTMSGSRSV1/INVSTMTTRNRS/INVSTMTRS/INVBAL/BALLIST/"
        )
        for balance in balances:
            if balance.find("./NAME").text == "Networth":
                acct_balance = float(balance.find("./VALUE").text)
                break

        return acct_balance
