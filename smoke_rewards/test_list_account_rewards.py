from utils.cli_wallet import CLI_WALLET
from utils.py_logger import log_step
from utils.account import create_account_with_balance
from utils.testutil import (calculate_account_reward_amount,
                            wait_blocks)
from utils.assets import (prepare_reward_user_asset_options,
                          create_new_user_asset)


def test_check_mfs_vesting_balance_with_zero_asset_rewards():

    log_step('Create new account without any asset rewards')
    account_1 = create_account_with_balance()

    log_step('Get mfs vesting balances of account_1')
    account_1_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        account_1.name)

    log_step('Check mfs vesting balances of account_1 is empty ')
    assert account_1_list_rewards == []


def test_check_mfs_vesting_balance_with_one_asset_reward(init_balances):
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 2000  # 2000 means 20%
    reward_percent = 1000  # 1000 means 10%
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent)
    asset_2_options = prepare_reward_user_asset_options(asset_2_percent,
                                                        reward_percent)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)
    asset_2 = create_new_user_asset('init2', precision,
                                    options=asset_2_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_2.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks(3)

    log_step('Get mfs vesting balances of referrer_1')
    referrer_1_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_1.name)

    log_step('Get expected referrer_1 reward')
    expected_referrer_1_reward = calculate_account_reward_amount(
        asset_2, asset_2_amount, asset_2_percent, reward_percent,
        acc1_ref_percent)

    log_step('Check if mfs vesting balances of referrer_1 is correct')
    asset_2_dict = {'asset_id': asset_2.id,
                    'amount': expected_referrer_1_reward}

    assert len(referrer_1_list_rewards) == 1

    mfs_vesting_balance = referrer_1_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_2_dict


def test_check_mfs_vesting_balance_after_reward_updates(init_balances):
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 2000  # 2000 means 20%
    reward_percent = 1000  # 1000 means 10%
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    sells_count = 2

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent)
    asset_2_options = prepare_reward_user_asset_options(asset_2_percent,
                                                        reward_percent)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)
    asset_2 = create_new_user_asset('init2', precision,
                                    options=asset_2_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_2.name)
    wait_blocks()

    log_step('Sell assets 2 times')
    for _ in xrange(sells_count):
        CLI_WALLET.sell_asset(
            account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
            asset_2.name, 300)
        CLI_WALLET.sell_asset(
            account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
            asset_1.name, 300)
    wait_blocks()

    log_step('Get mfs vesting balances of referrer_1')
    referrer_1_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_1.id)

    log_step('Get expected referrer_1 reward')
    expected_referrer_1_reward = calculate_account_reward_amount(
        asset_2, asset_2_amount, asset_2_percent, reward_percent,
        acc1_ref_percent)

    log_step('Check if mfs vesting balances of referrer_1 is correct')
    asset_2_dict = {'asset_id': asset_2.id,
                    'amount': expected_referrer_1_reward * sells_count}

    assert len(referrer_1_list_rewards) == 1

    mfs_vesting_balance = referrer_1_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_2_dict


def test_check_updated_mfs_vesting_balances_after_added_new_reward(
        init_balances):
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 2000  # 2000 means 20%
    reward_percent = 1000  # 1000 means 10%
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent)
    asset_2_options = prepare_reward_user_asset_options(asset_2_percent,
                                                        reward_percent)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)
    asset_2 = create_new_user_asset('init2', precision,
                                    options=asset_2_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_2.name)
    wait_blocks()

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_2.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Sell assets again')
    CLI_WALLET.sell_asset(
        account_1.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    wait_blocks()

    log_step('Get mfs vesting balances of referrer_1')
    referrer_1_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_1.name)

    exp_ref_1_asset_1_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        acc1_ref_percent)

    exp_ref_1_asset_2_reward = calculate_account_reward_amount(
        asset_2, asset_2_amount, asset_2_percent, reward_percent,
        acc1_ref_percent)

    log_step('Check if mfs vesting balances of referrer_1 is correct')
    assert len(referrer_1_list_rewards) == 2

    ref_1_asset_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_1.name,
                                                              asset_1.id)
    ref_1_asset_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_1.name,
                                                              asset_2.id)

    assert ref_1_asset_1_mfs_vb.asset_amount == exp_ref_1_asset_1_reward
    assert ref_1_asset_2_mfs_vb.asset_amount == exp_ref_1_asset_2_reward


def test_check_updated_mfs_vesting_balances_after_withdraw_vesting_reward(init_balances):  # noqa flake8
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 2000  # 2000 means 20%
    reward_percent = 1000  # 1000 means 10%
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent)
    asset_2_options = prepare_reward_user_asset_options(asset_2_percent,
                                                        reward_percent)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)
    asset_2 = create_new_user_asset('init2', precision,
                                    options=asset_2_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_2.name)
    wait_blocks()

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_2.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_1.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Sell assets again')
    CLI_WALLET.sell_asset(
        account_1.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    wait_blocks()

    log_step('Get referrer_1 assets rewards')
    ref_1_asset_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_1.id)

    ref_1_asset_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)

    log_step('Withdraw vesting asset_1 fee by referrer_1')
    CLI_WALLET.withdraw_vesting(ref_1_asset_1_mfs_vb.id, asset_1,
                                ref_1_asset_1_mfs_vb.asset_amount)
    wait_blocks()

    log_step('Check if mfs vesting balances of referrer_1 is correct')
    referrer_1_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_1.name)
    assert len(referrer_1_list_rewards) == 2

    current_ref_1_asset_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_1.id)
    assert current_ref_1_asset_1_mfs_vb.asset_amount == 0

    exp_ref_1_asset_2_reward = calculate_account_reward_amount(
        asset_2, asset_2_amount, asset_2_percent, reward_percent,
        acc1_ref_percent)
    assert ref_1_asset_2_mfs_vb.asset_amount == exp_ref_1_asset_2_reward

    log_step('Withdraw vesting asset_2 fee by referrer_1')
    CLI_WALLET.withdraw_vesting(ref_1_asset_2_mfs_vb.id, asset_2,
                                ref_1_asset_2_mfs_vb.asset_amount)
    wait_blocks()

    log_step('Check that mfs vesting balances of referrer_1 is empty')
    referrer_1_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer_1.name)
    assert len(referrer_1_list_rewards) == 2

    current_ref_1_asset_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)
    assert current_ref_1_asset_2_mfs_vb.asset_amount == 0


def test_check_list_account_rewards_with_wrong_values(init_balances):
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 2000  # 2000 means 20%
    reward_percent = 1000  # 1000 means 10%
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent)
    asset_2_options = prepare_reward_user_asset_options(asset_2_percent,
                                                        reward_percent)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)
    asset_2 = create_new_user_asset('init2', precision,
                                    options=asset_2_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_2.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Try to get mfs vesting balances of referrer_1')
    cases_list = ['%sx' % referrer_1.name,
                  'x%s' % referrer_1.name,
                  '',
                  asset_2.id]
    for case in cases_list:
        response = CLI_WALLET.try_send_request(
            "get_vesting_balances", [case])
        assert 'assert_exception' in response['error']['message']


def test_enumerate_2_rewards_on_referrer_vesting_balance(init_balances):
    precision = 1
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 2000  # 2000 means 20%
    reward_percent = 1000  # 1000 means 10%
    referrer_percent = 10
    amount_to_issue = 100000
    asset_1_amount = 4000
    asset_2_amount = 8000

    referrer = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer.name,
                                            referrer_percent=referrer_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer.name,
                                            referrer_percent=referrer_percent)

    log_step('Create 2 new user assets')
    asset_1_options = prepare_reward_user_asset_options(asset_1_percent,
                                                        reward_percent)
    asset_2_options = prepare_reward_user_asset_options(asset_2_percent,
                                                        reward_percent)

    asset_1 = create_new_user_asset('init1', precision,
                                    options=asset_1_options)
    asset_2 = create_new_user_asset('init2', precision,
                                    options=asset_2_options)

    log_step('Issue assets')
    CLI_WALLET.issue_asset(
        account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(
        account_2.name, amount_to_issue, asset_2.name)
    wait_blocks()

    log_step('Sell assets 2 times')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Get mfs vesting balances of referrer')
    referrer_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        referrer.id)

    log_step('Get expected referrer rewards')
    expected_referrer_asset_1_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        referrer_percent)
    expected_referrer_asset_2_reward = calculate_account_reward_amount(
        asset_2, asset_2_amount, asset_2_percent, reward_percent,
        referrer_percent)

    log_step('Check mfs vesting balances of referrer are correct')
    assets_list = (
        {'asset_id': asset_1.id, 'amount': expected_referrer_asset_1_reward},
        {'asset_id': asset_2.id, 'amount': expected_referrer_asset_2_reward}
    )

    assert len(referrer_list_rewards) == 2

    for mfs_vesting_balance in referrer_list_rewards:
        assert mfs_vesting_balance.allowed_withdraw in assets_list
