from testutil import generate_new_asset_name, wait_blocks
from cli_wallet import CLI_WALLET
from utils.py_logger import logger


class FbAsset(object):
    def __init__(self, registrar, precision=2, name=None):
        self.registrar = registrar
        self.precision = precision
        self.name = generate_new_asset_name().upper() if name is None else name
        self._id = None

    @property
    def id(self):
        if self._id is None:
            self._id = CLI_WALLET.get_asset_id_by_symbol(self.name)
        return self._id

    def create_asset(self, options):
        logger.info('Creating "%s" FB asset by %s. Precision: %s. Options: %s'
                    % (self.name, self.registrar, self.precision, options))
        response = CLI_WALLET.send_request(
            "create_asset",
            [self.registrar, self.name, self.precision, options, None, True])
        logger.info('Done.')
        return response

    def try_create_asset(self, options):
        logger.info(
            'Trying to create FB asset with following options: %s' % options)
        response = CLI_WALLET.try_send_request(
            "create_asset",
            [self.registrar, self.name, self.precision, options, None, True])
        return response

    def issue_asset(self, amount):
        logger.info('Issuing %s "%s" asset' % (amount, self.name))
        response = CLI_WALLET.send_request(
            "issue_asset", [self.registrar, amount, self.name, "", True])
        logger.info('Done.')
        return response

    def get_options(self):
        response = CLI_WALLET.send_request("get_asset", [self.name])
        return response["result"]["options"]

    def update_options(self, new_options):
        response = CLI_WALLET.update_asset(self.name, None, new_options)
        return response

    def try_update_options(self, new_options):
        logger.info(
            'Trying to update FBA with following options: %s' % new_options)
        response = CLI_WALLET.try_send_request(
            "update_asset", [self.name, None, new_options, True])
        return response

    def transfer_to(self, holder_name, amount):
        CLI_WALLET.transfer(
            self.registrar, holder_name, amount, asset=self.name)

    def get_revenue_assets(self):
        options = self.get_options()
        return options['additional_options']['revenue_assets']

    def get_accumulated_fees(self):
        accumulated_fees = CLI_WALLET.get_accumulated_fees(self.id)
        return accumulated_fees


def create_stock_asset(account_name, amount, precision, revenue_assets):
    options = prepare_fb_asset_options(revenue_assets)
    asset_name = generate_new_asset_name()

    fb_asset = FbAsset(account_name, precision, asset_name)

    fb_asset.create_asset(options)
    fb_asset.issue_asset(amount)
    wait_blocks()

    return fb_asset


def prepare_fb_asset_options(revenue_assets, market_fee_percent=0):
    """revenue_assets should be a list type"""
    options = {"max_supply": 1000000000,
               "market_fee_percent": market_fee_percent,
               "max_market_fee": 0,
               "issuer_permissions": 0,
               "flags": 0,
               "extensions": {
                   "revenue_assets": revenue_assets
               },
               "core_exchange_rate": {
                   "base": {
                       "amount": 10,
                       "asset_id": "1.3.0"},
                   "quote": {
                       "amount": 10,
                       "asset_id": "1.3.1"}},
               "whitelist_authorities": [],
               "blacklist_authorities": [],
               "whitelist_markets": [],
               "blacklist_markets": [],
               "description": "Test asset description"
               }
    return options
