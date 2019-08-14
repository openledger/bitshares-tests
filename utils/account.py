from testutil import (create_account_update_operation_auth,
                      generate_random_name, wait_blocks)
from utils.cli_wallet import CLI_WALLET
from utils.constants import DEFAULT_CORE_ASSET, PUBLIC_KEY, PRIVATE_KEY


class Account(object):
    def __init__(self, name=None, pub=PUBLIC_KEY, priv=PRIVATE_KEY):
        self.pub_key = pub
        self.priv_key = priv
        self.name = generate_random_name() if name is None else name
        self._id = None

    @property
    def id(self):
        if self._id is None:
            self._id = CLI_WALLET.get_account(self.name)['id']
        return self._id

    def sell_asset(self, amount_to_sell, symbol_to_sell, minimum_to_receive,
                   symbol_to_receive, timeout=600):
        CLI_WALLET.sell_asset(
            self.name, amount_to_sell, symbol_to_sell, minimum_to_receive,
            symbol_to_receive, timeout)

    def get_account_reward(self, asset_symbol):
        result = CLI_WALLET.get_mfs_vesting_balance(self.name, asset_symbol)
        return result

    def get_asset_account_balance(self, asset_name=DEFAULT_CORE_ASSET):
        result = CLI_WALLET.get_asset_account_balance(self.name, asset_name)
        return result

    def transfer(self, to_account, amount, asset_name=DEFAULT_CORE_ASSET):
        response = CLI_WALLET.transfer(self.name, to_account, amount,
                                       asset_name)
        return response

    def get_account_info(self):
        account_info = CLI_WALLET.get_account(self.name)
        return account_info

    def update_authorities(self, owner_weight_threshold,
                           owner_account_auths, active_weight_threshold,
                           active_account_auths):
        transaction_handle = CLI_WALLET.get_transaction_handle()
        acc_upd_op = create_account_update_operation_auth(
            self.id, owner_weight_threshold=owner_weight_threshold,
            owner_account_auths=owner_account_auths,
            active_weight_threshold=active_weight_threshold,
            active_account_auths=active_account_auths)
        CLI_WALLET.add_operation_to_builder_transaction(transaction_handle,
                                                        acc_upd_op)
        CLI_WALLET.set_fees_on_builder_transaction(transaction_handle)
        result = CLI_WALLET.sign_builder_transaction(transaction_handle)
        return result

    def get_mfs_vesting_balance(self, asset_id):
        balance = CLI_WALLET.get_mfs_vesting_balance(self.name, asset_id)
        return balance


def create_account_with_balance(balance='1000', registrar='nathan',
                                referrer='nathan', referrer_percent='0',
                                lifetime=False):
    new_account = Account()
    CLI_WALLET.register_account(
        new_account.name, new_account.pub_key, new_account.pub_key, registrar,
        referrer, referrer_percent)
    wait_blocks()
    CLI_WALLET.transfer('nathan', new_account.name, balance)
    wait_blocks()
    if lifetime:
        CLI_WALLET.upgrade_account(new_account.name)
        wait_blocks()
    return new_account
