# NOTE: If you are going to change some values in dictionaries below,
# you should perform deep copying by using "deepcopy" method from "copy" lib

from testutil import prepare_market_asset_options, wait_blocks
from cli_wallet import CLI_WALLET
from py_logger import logger
from user_asset import UserAsset


ASSET_PERMISSIONS = {
    "charge_market_fee": True,
    "white_list": True,
    "override_authority": True,
    "transfer_restricted": True,
    "disable_force_settle": True,
    "global_settle": True,
    "disable_confidential": True,
    "witness_fed_asset": True,
    "committee_fed_asset": True,
}


ASSET_FLAGS = {
    "charge_market_fee": False,
    "white_list": False,
    "override_authority": False,
    "transfer_restricted": False,
    "disable_force_settle": False,
    "global_settle": False,
    "disable_confidential": False,
    "witness_fed_asset": False,
    "committee_fed_asset": True,
}


def prepare_reward_marked_asset_options(asset_percent, reward_percent):
    # market_fee_percent: value 100 is 1%
    # reward_percent: value 100 is 1%
    # flags 257 include charge_market_fee, that allows to take fee
    options = {
        "max_supply": 10000000000,
        "market_fee_percent": asset_percent,
        "max_market_fee": 1000000000,
        "issuer_permissions": 511,
        "flags": 257,
        "extensions": {
            "reward_percent": reward_percent
        },
        "core_exchange_rate": {
            "base": {
                "amount": 1,
                "asset_id": "1.3.0"
            },
            "quote": {
                "amount": 1,
                "asset_id": "1.3.1"
            }
        },
        "whitelist_authorities": [],
        "blacklist_authorities": [],
        "whitelist_markets": [],
        "blacklist_markets": [],
        "description": "asset description"
    }
    return options


def prepare_reward_user_asset_options(asset_percent, reward_percent,
                                      mfs_whitelist=None):
    # market_fee_percent: value 100 is 1%
    # reward_percent: value 100 is 1%
    options = {
        "max_supply": 1000000000,
        "market_fee_percent": asset_percent,
        "max_market_fee": 100000000,
        "issuer_permissions": 0,
        "flags": 1,
        "extensions": {
            "reward_percent": reward_percent
        },
        "core_exchange_rate": {
            "base": {
                "amount": 1,
                "asset_id":
                    "1.3.0"
            },
            "quote": {
                "amount": 1,
                "asset_id": "1.3.1"
            }
        },
        "whitelist_authorities": [],
        "blacklist_authorities": [],
        "whitelist_markets": [],
        "blacklist_markets": [],
        "description": "user asset description"
    }
    if mfs_whitelist is not None:
        options['extensions']['whitelist_market_fee_sharing'] = mfs_whitelist
    return options


def prepare_whitelist_user_asset_options(asset_percent, reward_percent,
                                         mfs_whitelist=None, whitelist=None,
                                         blacklist=None):
    # market_fee_percent: value 100 is 1%
    # reward_percent: value 100 is 1%
    # "issuer_permissions": 2 and "flags": 3 means turned on
    # whitelist_authorities and blacklist_authorities options
    options = {
        "max_supply": 1000000000,
        "market_fee_percent": asset_percent,
        "max_market_fee": 100000000,
        "issuer_permissions": 2,
        "flags": 3,
        "extensions": {
            "reward_percent": reward_percent
        },
        "core_exchange_rate": {
            "base": {
                "amount": 1,
                "asset_id":
                    "1.3.0"
            },
            "quote": {
                "amount": 1,
                "asset_id": "1.3.1"
            }
        },
        "whitelist_authorities": [],
        "blacklist_authorities": [],
        "whitelist_markets": [],
        "blacklist_markets": [],
        "description": "user asset description"
    }
    if mfs_whitelist is not None:
        options['extensions']['whitelist_market_fee_sharing'] = mfs_whitelist
    if whitelist is not None:
        options['whitelist_authorities'] = whitelist
    if blacklist is not None:
        options['blacklist_authorities'] = blacklist
    return options


def prepare_user_asset_options(asset_percent):
    # market_fee_percent: value 100 is 1%
    options = {
        "max_supply": 1000000000,
        "market_fee_percent": asset_percent,
        "max_market_fee": 100000000,
        "issuer_permissions": 0,
        "flags": 1,
        "core_exchange_rate": {
            "base": {
                "amount": 1,
                "asset_id":
                    "1.3.0"
            },
            "quote": {
                "amount": 1,
                "asset_id": "1.3.1"
            }
        },
        "whitelist_authorities": [],
        "blacklist_authorities": [],
        "whitelist_markets": [],
        "blacklist_markets": [],
        "description": "user asset description"
    }
    return options


def create_new_user_asset(account_name, precision, asset_name=None,
                          options=None):
    # account should be a committee member
    # account should have enough balance
    logger.info('Creating new user asset...')
    options = prepare_market_asset_options(ASSET_PERMISSIONS, ASSET_FLAGS) \
        if options is None else options

    asset = UserAsset(account_name, precision, asset_name)

    # create user asset
    asset.create_asset(options)
    wait_blocks()
    logger.info(
        'New user asset created. Name: %s. ID: %s' % (asset.name, asset.id))
    return asset


def publish_asset_feed(account_name, asset_name, asset_id):
    core_asset_id = str(CLI_WALLET.get_asset_id_by_symbol("BTS"))
    price_feed = {
        "core_exchange_rate":
            {
                "base": {
                    "amount": 1,
                    "asset_id": asset_id
                },
                "quote": {
                    "amount": 1,
                    "asset_id": core_asset_id
                }
            },
        "settlement_price":
            {
                "base": {
                    "amount": 1,
                    "asset_id": asset_id
                },
                "quote": {
                    "amount": 1,
                    "asset_id": core_asset_id
                }
            }
    }
    CLI_WALLET.publish_asset_feed(account_name, asset_name, price_feed)
