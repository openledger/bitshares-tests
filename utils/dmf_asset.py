from testutil import (prepare_dmf_asset_options, wait_blocks,
                      generate_new_asset_name)
from cli_wallet import CLI_WALLET
from base_asset import Asset
from utils.constants import DEFAULT_EXTENSIONS, DMF_ASSET_FLAG


class DMFAsset(Asset):
    def __init__(self, registrar, precision=1, name=None):
        super(DMFAsset, self).__init__(registrar, precision=precision,
                                       name=name)

    def create_asset(self, options):
        response = CLI_WALLET.send_request(
            "create_asset", [self.registrar, self.name, self.precision,
                             options, None, True])
        return response

    def try_create_asset(self, options):
        response = CLI_WALLET.try_send_request(
            "create_asset", [self.registrar, self.name, self.precision,
                             options, None, True])
        return response


def create_dmf_asset(account_name, balance, precision=0, asset_name=None,
                     extensions=None):
    extensions = DEFAULT_EXTENSIONS if extensions is None else extensions
    options = prepare_dmf_asset_options(extensions, flags_int=DMF_ASSET_FLAG)

    dmf_name = generate_new_asset_name() if asset_name is None else asset_name
    dmf_asset = DMFAsset(account_name, precision, dmf_name)

    dmf_asset.create_asset(options)
    dmf_asset.issue_asset(balance)
    wait_blocks(1)

    return dmf_asset
