from testutil import prepare_asset_options, asset_exists, wait_blocks
from cli_wallet import CLI_WALLET
from base_asset import Asset


class UserAsset(Asset):
    def __init__(self, registrar, precision=1, name=None):
        super(UserAsset, self).__init__(registrar, precision=precision,
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


def create_user_asset(account_name, balance, precision, asset_name=None,
                      options=None, permissions_int=0):
    options = prepare_asset_options(permissions_int, 0) if options is None \
        else options

    user_asset = UserAsset(account_name, precision, asset_name)

    if asset_exists(user_asset.name):
        return user_asset

    user_asset.create_asset(options)
    user_asset.issue_asset(balance)
    wait_blocks(1)

    return user_asset
