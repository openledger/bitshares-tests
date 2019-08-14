from cli_wallet import CLI_WALLET
from assets import (prepare_market_asset_options, ASSET_PERMISSIONS,
                    ASSET_FLAGS)
from testutil import wait_blocks
from py_logger import logger
from base_asset import Asset


class MarketAsset(Asset):
    def __init__(self, registrar, precision=1, name=None):
        super(MarketAsset, self).__init__(registrar, precision=precision,
                                          name=name)

    def create_asset(self, options):
        response = CLI_WALLET.send_request(
            "create_asset", [self.registrar, self.name, self.precision,
                             options, {}, True])
        return response

    def try_create_asset(self, options):
        response = CLI_WALLET.try_send_request(
            "create_asset", [self.registrar, self.name, self.precision,
                             options, {}, True])
        return response


def create_market_asset(account_name, precision, asset_name=None,
                        options=None):
    # account should be a committee member
    # account should have enough balance
    logger.info('Creating new market asset...')
    options = prepare_market_asset_options(ASSET_PERMISSIONS, ASSET_FLAGS) \
        if options is None else options

    asset = MarketAsset(account_name, precision, asset_name)

    # create market asset
    asset.create_asset(options)
    wait_blocks()
    logger.info(
        'New market asset created. Name: %s. ID: %s' % (asset_name, asset.id))
    return asset
