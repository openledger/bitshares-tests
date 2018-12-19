import pytest
from utils.cli_wallet import CLI_WALLET
from utils.py_logger import log_step
from utils.account import create_account_with_balance, Account
from utils.testutil import (calculate_account_reward_amount,
                            wait_blocks)
from utils.assets import (prepare_reward_user_asset_options,
                          create_new_user_asset)
from utils.constants import DEFAULT_CORE_ASSET
from utils.user_asset import UserAsset


def test_add_registrar_to_mfs_whitelist_and_check_registrar_reward(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2_percent = 100 - ref_2_percent

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    asset_1_mfs_whitelist = [registrar_2.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Get mfs vesting balances list of registrar_2')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        registrar_2.name)

    log_step('Get expected registrar_2 reward')
    expected_registrar_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        registrar_2_percent)

    log_step('Check mfs vesting balances of registrar_2 is correct')
    asset_1_dict = {'asset_id': asset_1.id,
                    'amount': expected_registrar_2_reward}

    assert len(registrar_2_list_rewards) == 1

    mfs_vesting_balance = registrar_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict


def test_add_registrar_to_mfs_whitelist_and_check_referrer_reward(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    asset_1_mfs_whitelist = [registrar_2.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Get mfs vesting balances list of referrer_2')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_2.name)

    log_step('Get expected referrer_2 reward')
    expected_referrer_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        ref_2_percent)

    log_step('Check mfs vesting balances of referrer_2 is correct')
    asset_1_dict = {'asset_id': asset_1.id,
                    'amount': expected_referrer_2_reward}

    assert len(referrer_2_list_rewards) == 1

    mfs_vesting_balance = referrer_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict


def test_add_referrer_to_mfs_whitelist_and_check_all_rewards(init_balances):
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    asset_1_mfs_whitelist = [referrer_2.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Check mfs vesting balances of registrar_2 is empty')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        registrar_2.name)

    assert registrar_2_list_rewards == []

    log_step('Check mfs vesting balances of referrer_2 is empty')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_2.name)

    assert referrer_2_list_rewards == []


def test_referrer_has_100_reward_percents_and_registrar_is_in_mfs_whitelist(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 100
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    asset_1_mfs_whitelist = [registrar_2.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Get mfs vesting balances list of referrer_2')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_2.name)

    log_step('Calculate expected referrer_2 reward')
    expected_referrer_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        ref_2_percent)

    log_step('Check mfs vesting balances for referrer_2 is correct')
    asset_1_dict = {'asset_id': asset_1.id,
                    'amount': expected_referrer_2_reward}

    assert len(referrer_2_list_rewards) == 1

    mfs_vesting_balance = referrer_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict


def test_referrer_has_0_reward_percents_and_registrar_is_in_mfs_whitelist(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 0
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    asset_1_mfs_whitelist = [registrar_2.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Check mfs vesting balances list of referrer_2 is empty')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_2.name)

    assert referrer_2_list_rewards == []


@pytest.mark.parametrize('referrer_percent', [100, 0])
def test_referrer_has_0_or_100_reward_percents_and_referrer_is_in_mfs_whitelist(init_balances, referrer_percent):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = referrer_percent
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    asset_1_mfs_whitelist = [referrer_2.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Check mfs vesting balances of registrar_2 is empty')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        registrar_2.name)

    assert registrar_2_list_rewards == []

    log_step('Check mfs vesting balances of referrer_2 is empty')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_2.name)

    assert referrer_2_list_rewards == []


def test_add_1_of_2_registrars_to_mfs_whitelist_and_check_rewards(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_1_percent = 10
    ref_2_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_1 = create_account_with_balance(20000, lifetime=True)
    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_1.name,
                                            referrer=referrer_1.name,
                                            referrer_percent=ref_1_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    asset_1_mfs_whitelist = [registrar_2.id]

    log_step('Create 2 new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets by 2 accounts')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets twice')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)

    CLI_WALLET.sell_asset(
        account_2.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_1.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Get mfs vesting balances list of referrer_2')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_2.name)

    log_step('Get expected referrer_2 reward')
    expected_referrer_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        ref_2_percent)

    log_step('Check mfs vesting balances of referrer_2 is correct')
    asset_1_dict = {'asset_id': asset_1.id,
                    'amount': expected_referrer_2_reward}

    assert len(referrer_2_list_rewards) == 1

    mfs_vesting_balance = referrer_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict

    log_step('Check mfs vesting balances of referrer_1 is empty')
    referrer_1_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_1.name)

    assert referrer_1_list_rewards == []


@pytest.mark.parametrize('case', ['', 'wrong_value', '1.3.0', 'init2'])
def test_try_to_create_asset_with_wrong_value_in_mfs_whitelist(init_balances, case):  # noqa flake8
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%

    asset_1_mfs_whitelist = [case]
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset = UserAsset('init1')

    log_step('Try to creating new user asset')
    result = asset.try_create_asset(asset_1_options)
    assert 'error' in result


def test_remove_account_from_mfs_whitelist_by_updating_asset_so_mfs_whitelist_is_empty(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2_percent = 100 - ref_2_percent

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    init0 = Account('init0')
    asset_1_mfs_whitelist = [init0.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Remove init0 from asset whitelist')
    current_options = asset_1.get_options()
    current_options['extensions']['whitelist_market_fee_sharing'] = []
    asset_1.update_options(current_options)

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Get mfs vesting balances list of registrar_2')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        registrar_2.name)

    log_step('Get expected registrar_2 reward')
    expected_registrar_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        registrar_2_percent)

    log_step('Check mfs vesting balances of registrar_2 is correct')
    asset_1_dict = {'asset_id': asset_1.id,
                    'amount': expected_registrar_2_reward}

    assert len(registrar_2_list_rewards) == 1

    mfs_vesting_balance = registrar_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict


def test_add_account_to_mfs_whitelist_by_updating_asset(init_balances):
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2_percent = 100 - ref_2_percent

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    init0 = Account('init0')
    asset_1_mfs_whitelist = [init0.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Add registrar_2 to asset whitelist')
    new_mfs_whitelist = [init0.id, registrar_2.id]
    current_options = asset_1.get_options()
    current_options['extensions']['whitelist_market_fee_sharing'] = \
        new_mfs_whitelist
    asset_1.update_options(current_options)

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Get mfs vesting balances list of registrar_2')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        registrar_2.name)

    log_step('Get expected registrar_2 reward')
    expected_registrar_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        registrar_2_percent)

    log_step('Check mfs vesting balances of registrar_2 is correct')
    asset_1_dict = {'asset_id': asset_1.id,
                    'amount': expected_registrar_2_reward}

    assert len(registrar_2_list_rewards) == 1

    mfs_vesting_balance = registrar_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict


def test_remove_account_from_mfs_whitelist_so_account_can_not_get_reward(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    ref_2_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    registrar_2 = create_account_with_balance(20000, lifetime=True)

    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000)
    account_2 = create_account_with_balance(balance=1000000,
                                            registrar=registrar_2.name,
                                            referrer=referrer_2.name,
                                            referrer_percent=ref_2_percent)

    init0 = Account('init0')
    asset_1_mfs_whitelist = [init0.id, registrar_2.id]

    log_step('Create new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent,
                                                        asset_1_mfs_whitelist)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Remove registrar_2 from asset whitelist')
    current_options = asset_1.get_options()
    new_mfs_whitelist = [init0.id]
    current_options['extensions']['whitelist_market_fee_sharing'] = \
        new_mfs_whitelist
    asset_1.update_options(current_options)

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        DEFAULT_CORE_ASSET, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, DEFAULT_CORE_ASSET, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Check mfs vesting balances list of registrar_2 is empty')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        registrar_2.name)

    assert registrar_2_list_rewards == []
