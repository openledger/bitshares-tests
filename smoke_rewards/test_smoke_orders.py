from utils.cli_wallet import CLI_WALLET
from utils.py_logger import log_step, logger
from utils.account import create_account_with_balance
from utils.testutil import (calculate_percent, wait_blocks)
from utils.assets import (prepare_reward_user_asset_options,
                          create_new_user_asset)


def test_check_partial_order_matching(committee):
    precision = 0
    precision_value = 10 ** precision
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    amount_to_issue = 10000

    acc1_asset_1_amount_to_sell = 2000
    acc1_asset_2_amount_to_buy = 1000

    acc2_asset_2_amount_to_sell = 1000
    acc2_asset_1_amount_to_buy = 1000

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

    log_step('Sell assets from account_2')
    CLI_WALLET.sell_asset(
        account_2.name, acc2_asset_2_amount_to_sell, asset_2.name,
        acc2_asset_1_amount_to_buy, asset_1.name, 60)

    log_step('Check current limit orders')
    orders_before = CLI_WALLET.get_limit_orders(asset_1.id, asset_2.id)
    assert len(orders_before) == 1

    log_step('Sell assets from account_1')
    CLI_WALLET.sell_asset(
        account_1.name, acc1_asset_1_amount_to_sell, asset_1.name,
        acc1_asset_2_amount_to_buy, asset_2.name, 60)
    wait_blocks()

    log_step('Check current limit orders')
    orders_after = CLI_WALLET.get_limit_orders(asset_1.id, asset_2.id)

    logger.info('Check that current order is only one')
    assert len(orders_after) == 1

    logger.info('Check that current order is not previous order')
    assert orders_after[0]['id'] > orders_before[0]['id']

    log_step('Check that new order amount to sell is equal to 1000 asset')
    assert orders_after[0]['for_sale'] == 1000

    log_step('Calculate assets rewards')
    asset_1_full_fee = calculate_percent(
        acc2_asset_1_amount_to_buy * precision_value, asset_1_percent)
    asset_2_full_fee = calculate_percent(
        acc1_asset_2_amount_to_buy * precision_value, asset_2_percent)

    log_step('Check accounts balances')
    acc2_balances = CLI_WALLET.get_dict_account_balance(account_2.name)
    acc1_balances = CLI_WALLET.get_dict_account_balance(account_1.name)

    exp_acc2_asset_2_balance = amount_to_issue - acc2_asset_2_amount_to_sell
    exp_acc2_asset_1_balance = acc2_asset_1_amount_to_buy - asset_1_full_fee
    assert acc2_balances[asset_2.id] == exp_acc2_asset_2_balance
    assert acc2_balances[asset_1.id] == exp_acc2_asset_1_balance

    exp_acc1_asset_1_balance = amount_to_issue - acc1_asset_1_amount_to_sell
    exp_acc1_asset_2_balance = acc1_asset_2_amount_to_buy - asset_2_full_fee
    assert acc1_balances[asset_1.id] == exp_acc1_asset_1_balance
    assert acc1_balances[asset_2.id] == exp_acc1_asset_2_balance

    log_step('Calculate assets reward amounts')
    asset_1_reward_amount = calculate_percent(asset_1_full_fee, reward_percent)
    asset_2_reward_amount = calculate_percent(asset_2_full_fee, reward_percent)

    log_step('Check referrers asset rewards')
    referrer_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_1.name,
                                                           asset_2.id)
    referrer_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_2.name,
                                                           asset_1.id)

    expected_referrer_1_reward = calculate_percent(asset_2_reward_amount,
                                                   acc1_ref_percent,
                                                   bitshares_value=False)
    expected_referrer_2_reward = calculate_percent(asset_1_reward_amount,
                                                   acc2_ref_percent,
                                                   bitshares_value=False)

    assert referrer_1_mfs_vb.asset_amount == expected_referrer_1_reward
    assert referrer_2_mfs_vb.asset_amount == expected_referrer_2_reward

    log_step('Check registrars asset rewards')
    registrar_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                            asset_2.id)
    registrar_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                            asset_1.id)

    exp_reg_1_reward = asset_2_reward_amount - referrer_1_mfs_vb.asset_amount
    exp_reg_2_reward = asset_1_reward_amount - referrer_2_mfs_vb.asset_amount

    assert registrar_1_mfs_vb.asset_amount == exp_reg_1_reward
    assert registrar_2_mfs_vb.asset_amount == exp_reg_2_reward


def test_check_full_order_matching(committee):
    precision = 0
    precision_value = 10 ** precision
    asset_1_percent = 1000  # 1000 means 10%
    asset_2_percent = 1000  # 1000 means 10%
    reward_percent = 1000  # 1000 means 10%
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    amount_to_issue = 10000

    acc1_asset_1_amount_to_sell = 2000
    acc1_asset_2_amount_to_buy = 1000

    acc2_asset_2_amount_to_sell = 1000
    acc2_asset_1_amount_to_buy = 1000

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

    log_step('Sell assets: First account_1 then account_2')
    CLI_WALLET.sell_asset(
        account_1.name, acc1_asset_1_amount_to_sell, asset_1.name,
        acc1_asset_2_amount_to_buy, asset_2.name, 30)
    CLI_WALLET.sell_asset(
        account_2.name, acc2_asset_2_amount_to_sell, asset_2.name,
        acc2_asset_1_amount_to_buy, asset_1.name, 30)
    wait_blocks()

    log_step('Check current limit orders')
    limit_orders = CLI_WALLET.get_limit_orders(asset_1.id, asset_2.id)
    assert limit_orders == []

    log_step('Calculate assets rewards')
    asset_1_full_fee = calculate_percent(
        acc1_asset_1_amount_to_sell * precision_value, asset_1_percent)
    asset_2_full_fee = calculate_percent(
        acc1_asset_2_amount_to_buy * precision_value, asset_2_percent)

    log_step('Check accounts balances')
    acc1_balances = CLI_WALLET.get_dict_account_balance(account_1.name)
    acc2_balances = CLI_WALLET.get_dict_account_balance(account_2.name)
    exp_acc1_asset_1_balance = amount_to_issue - acc1_asset_1_amount_to_sell
    exp_acc1_asset_2_balance = acc1_asset_2_amount_to_buy - asset_2_full_fee
    assert acc1_balances[asset_1.id] == exp_acc1_asset_1_balance
    assert acc1_balances[asset_2.id] == exp_acc1_asset_2_balance

    exp_acc2_asset_2_balance = amount_to_issue - acc2_asset_2_amount_to_sell
    exp_acc2_asset_1_balance = acc1_asset_1_amount_to_sell - asset_1_full_fee
    assert acc2_balances[asset_2.id] == exp_acc2_asset_2_balance
    assert acc2_balances[asset_1.id] == exp_acc2_asset_1_balance
