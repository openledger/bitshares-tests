from utils.cli_wallet import CLI_WALLET
from utils.py_logger import log_step, logger
from utils.account import create_account_with_balance
from utils.testutil import wait_blocks, calculate_account_reward_amount
from utils.assets import (prepare_whitelist_user_asset_options,
                          create_new_user_asset)
from utils.constants import DEFAULT_CORE_ASSET


class WhitelistTcManager(object):

    def __init__(self):
        self.precision = 1
        self.asset_1_percent = 1000  # 1000 means 10%
        self.reward_percent = 1000  # 1000 means 10%
        self.ref_2_percent = 10
        self.reg_2_percent = 100 - self.ref_2_percent
        self.amount_to_issue = 100000
        self.asset_1_amount = 4000
        self.asset_2_amount = 8000
        self.authorized_account = None
        self.registrar_2 = None
        self.referrer_2 = None
        self.account_1 = None
        self.account_2 = None
        self.asset_1 = None

    def prepare_accounts(self):
        self.authorized_account = create_account_with_balance(300000,
                                                              lifetime=True)
        self.registrar_2 = create_account_with_balance(20000,
                                                       lifetime=True)
        self.referrer_2 = create_account_with_balance(20000, lifetime=True)

        self.account_1 = create_account_with_balance(balance=1000000)
        self.account_2 = create_account_with_balance(
            balance=1000000, registrar=self.registrar_2.name,
            referrer=self.referrer_2.name, referrer_percent=self.ref_2_percent)

    def create_new_user_asset(self):
        log_step('Create new user assets')
        whitelist_authorities = [self.authorized_account.id]
        blacklist_authorities = [self.authorized_account.id]
        asset_1_options = prepare_whitelist_user_asset_options(
            self.asset_1_percent, self.reward_percent,
            whitelist=whitelist_authorities, blacklist=blacklist_authorities)

        self.asset_1 = create_new_user_asset(self.authorized_account.name,
                                             self.precision,
                                             options=asset_1_options)

    def update_mfs_whitelist(self, new_mfs_whitelist):
        logger.info('Updating mfs whitelist to %s' % new_mfs_whitelist)
        current_options = self.asset_1.get_options()
        current_options['extensions']['whitelist_market_fee_sharing'] = \
            new_mfs_whitelist
        self.asset_1.update_options(current_options)

    def check_if_reward_amount_is_correct(self, account_name,
                                          reg_or_ref_percent):
        log_step('Get mfs vesting balances list of "%s"' % account_name)
        account_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
            account_name)

        log_step(
            'Calculate expected "%s" reward' % account_name)
        expected_account_reward = calculate_account_reward_amount(
            self.asset_1, self.asset_1_amount, self.asset_1_percent,
            self.reward_percent, reg_or_ref_percent)

        log_step('Check mfs vesting balances of registrar_2 is correct')
        asset_1_dict = {'asset_id': self.asset_1.id,
                        'amount': expected_account_reward}

        assert len(account_list_rewards) == 1

        mfs_vesting_balance = account_list_rewards[0]
        assert mfs_vesting_balance.allowed_withdraw == asset_1_dict

    def issue_and_sell_assets(self):
        log_step('Issue assets')
        CLI_WALLET.issue_asset(
            self.account_1.name, self.amount_to_issue, self.asset_1.name)
        wait_blocks()

        log_step('Sell assets')
        CLI_WALLET.sell_asset(self.account_1.name, self.asset_1_amount,
                              self.asset_1.name, self.asset_2_amount,
                              DEFAULT_CORE_ASSET, 300)
        CLI_WALLET.sell_asset(self.account_2.name, self.asset_2_amount,
                              DEFAULT_CORE_ASSET, self.asset_1_amount,
                              self.asset_1.name, 300)
        wait_blocks(3)

    def set_whitelist(self, account_name):
        log_step('Add "%s" to asset whitelist' % account_name)
        CLI_WALLET.whitelist_account(
            self.authorized_account.name, account_name, 'white_listed')

    def set_blacklist(self, account_name):
        log_step('Add "%s" to asset blacklist' % account_name)
        CLI_WALLET.whitelist_account(
            self.authorized_account.name, account_name, 'black_listed')
