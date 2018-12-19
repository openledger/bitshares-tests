from utils.cli_wallet import CLI_WALLET
from utils.py_logger import log_step, logger
from utils.account import create_account_with_balance
from utils.assets import (prepare_reward_marked_asset_options,
                          publish_asset_feed)
from utils.testutil import (calculate_account_reward_amount, wait_blocks,
                            calculate_percent)
from utils.market_asset import create_market_asset


def test_check_that_market_assets_transferred_when_order_was_closed(committee):
    precision = 0
    asset_1_percent = 100  # 100 means 1%
    asset_2_percent = 200  # 200 means 2%
    reward_percent = 100  # 100 means 1%
    amount_to_borrow = 10000000
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    asset_1_amount = 400000
    asset_2_amount = 800000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new market assets')
    asset_1_options = prepare_reward_marked_asset_options(asset_1_percent,
                                                          reward_percent)
    asset_2_options = prepare_reward_marked_asset_options(asset_2_percent,
                                                          reward_percent)

    asset_1 = create_market_asset('init1', precision, options=asset_1_options)
    asset_2 = create_market_asset('init2', precision, options=asset_2_options)

    log_step('Publish assets feed')
    publish_asset_feed('init1', asset_1.name, asset_1.id)
    publish_asset_feed('init2', asset_2.name, asset_2.id)
    wait_blocks()

    log_step('Borrow assets')
    CLI_WALLET.borrow_asset(
        account_1.name, amount_to_borrow, asset_1.name, '1000')
    CLI_WALLET.borrow_asset(
        account_2.name, amount_to_borrow, asset_2.name, '4000')
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Get accounts balances after sales')
    acc1_balance_after = CLI_WALLET.get_dict_account_balance(account_1.name)
    acc2_balance_after = CLI_WALLET.get_dict_account_balance(account_2.name)

    log_step('Check sellers balances after sales')
    asset_1_full_fee = calculate_percent(
        asset_1_amount * 10 ** precision, asset_1_percent)
    asset_2_full_fee = calculate_percent(
        asset_2_amount * 10 ** precision, asset_2_percent)
    logger.info('%s asset full fee: %s' % (asset_1.name, asset_1_full_fee))
    logger.info('%s asset full fee: %s' % (asset_2.name, asset_2_full_fee))
    assert acc1_balance_after[asset_2.id] == (
            asset_2_amount * (10 ** precision) - asset_2_full_fee)
    assert acc2_balance_after[asset_1.id] == (
            asset_1_amount * (10 ** precision) - asset_1_full_fee)


def test_check_accumulated_fees_after_order_was_closed(committee):
    precision = 0
    asset_1_percent = 100  # 100 means 1%
    asset_2_percent = 200  # 200 means 2%
    reward_percent = 100  # 100 means 1%
    amount_to_borrow = 10000000
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    asset_1_amount = 400000
    asset_2_amount = 800000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new market assets')
    asset_1_options = prepare_reward_marked_asset_options(asset_1_percent,
                                                          reward_percent)
    asset_2_options = prepare_reward_marked_asset_options(asset_2_percent,
                                                          reward_percent)

    asset_1 = create_market_asset('init1', precision, options=asset_1_options)
    asset_2 = create_market_asset('init2', precision, options=asset_2_options)

    log_step('Publish assets feed')
    publish_asset_feed('init1', asset_1.name, asset_1.id)
    publish_asset_feed('init2', asset_2.name, asset_2.id)
    wait_blocks()

    log_step('Borrow assets')
    CLI_WALLET.borrow_asset(
        account_1.name, amount_to_borrow, asset_1.name, '1000')
    CLI_WALLET.borrow_asset(
        account_2.name, amount_to_borrow, asset_2.name, '4000')
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Calculate assets full fee')
    asset_1_full_fee = calculate_percent(
        asset_1_amount * 10 ** precision, asset_1_percent)
    asset_2_full_fee = calculate_percent(
        asset_2_amount * 10 ** precision, asset_2_percent)
    logger.info('%s asset full fee: %s' % (asset_1.name, asset_1_full_fee))
    logger.info('%s asset full fee: %s' % (asset_2.name, asset_2_full_fee))

    log_step('Calculate assets reward amount')
    asset_1_reward_amount = calculate_percent(asset_1_full_fee, reward_percent)
    asset_2_reward_amount = calculate_percent(asset_2_full_fee, reward_percent)

    log_step('Check accumulated_fees')
    asset_1_accumulated_fees = CLI_WALLET.get_accumulated_fees(asset_1.id)
    asset_2_accumulated_fees = CLI_WALLET.get_accumulated_fees(asset_2.id)
    assert asset_1_accumulated_fees == asset_1_full_fee - asset_1_reward_amount
    assert asset_2_accumulated_fees == asset_2_full_fee - asset_2_reward_amount


def test_check_referrer_asset_reward(committee):
    precision = 0
    asset_1_percent = 100  # 100 means 1%
    asset_2_percent = 200  # 200 means 2%
    reward_percent = 100  # 100 means 1%
    amount_to_borrow = 10000000
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    asset_1_amount = 400000
    asset_2_amount = 800000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new market assets')
    asset_1_options = prepare_reward_marked_asset_options(asset_1_percent,
                                                          reward_percent)
    asset_2_options = prepare_reward_marked_asset_options(asset_2_percent,
                                                          reward_percent)

    asset_1 = create_market_asset('init1', precision, options=asset_1_options)
    asset_2 = create_market_asset('init2', precision, options=asset_2_options)

    log_step('Publish assets feed')
    publish_asset_feed('init1', asset_1.name, asset_1.id)
    publish_asset_feed('init2', asset_2.name, asset_2.id)
    wait_blocks()

    log_step('Borrow assets')
    CLI_WALLET.borrow_asset(
        account_1.name, amount_to_borrow, asset_1.name, '1000')
    CLI_WALLET.borrow_asset(
        account_2.name, amount_to_borrow, asset_2.name, '4000')
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Check referrers asset rewards')
    expected_referrer_1_reward = calculate_account_reward_amount(
        asset_2, asset_2_amount, asset_2_percent, reward_percent,
        acc1_ref_percent)
    expected_referrer_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        acc2_ref_percent)

    referrer_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_1.name,
                                                           asset_2.id)
    referrer_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_2.name,
                                                           asset_1.id)

    assert referrer_1_mfs_vb.asset_amount == expected_referrer_1_reward
    assert referrer_2_mfs_vb.asset_amount == expected_referrer_2_reward


def test_check_registrar_asset_reward(committee):
    precision = 0
    asset_1_percent = 100  # 100 means 1%
    asset_2_percent = 200  # 200 means 2%
    reward_percent = 100  # 100 means 1%
    amount_to_borrow = 10000000
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    asset_1_amount = 400000
    asset_2_amount = 800000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new market assets')
    asset_1_options = prepare_reward_marked_asset_options(asset_1_percent,
                                                          reward_percent)
    asset_2_options = prepare_reward_marked_asset_options(asset_2_percent,
                                                          reward_percent)

    asset_1 = create_market_asset('init1', precision, options=asset_1_options)
    asset_2 = create_market_asset('init2', precision, options=asset_2_options)

    log_step('Publish assets feed')
    publish_asset_feed('init1', asset_1.name, asset_1.id)
    publish_asset_feed('init2', asset_2.name, asset_2.id)
    wait_blocks()

    log_step('Borrow assets')
    CLI_WALLET.borrow_asset(
        account_1.name, amount_to_borrow, asset_1.name, '1000')
    CLI_WALLET.borrow_asset(
        account_2.name, amount_to_borrow, asset_2.name, '4000')
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Calculate registrars asset rewards')
    acc1_registrar_percent = 100 - acc1_ref_percent
    acc2_registrar_percent = 100 - acc2_ref_percent

    expected_registrar_1_reward = calculate_account_reward_amount(
        asset_2, asset_2_amount, asset_2_percent, reward_percent,
        acc1_registrar_percent)
    expected_registrar_2_reward = calculate_account_reward_amount(
        asset_1, asset_1_amount, asset_1_percent, reward_percent,
        acc2_registrar_percent)

    log_step('Check registrars asset rewards')
    registrar_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                            asset_2.id)
    registrar_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                            asset_1.id)

    assert registrar_1_mfs_vb.asset_amount == expected_registrar_1_reward
    assert registrar_2_mfs_vb.asset_amount == expected_registrar_2_reward


def test_check_withdraw_vesting_by_referrer(committee):
    precision = 0
    asset_1_percent = 100  # 100 means 1%
    asset_2_percent = 200  # 200 means 2%
    reward_percent = 100  # 100 means 1%
    amount_to_borrow = 10000000
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    asset_1_amount = 400000
    asset_2_amount = 800000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new market assets')
    asset_1_options = prepare_reward_marked_asset_options(asset_1_percent,
                                                          reward_percent)
    asset_2_options = prepare_reward_marked_asset_options(asset_2_percent,
                                                          reward_percent)

    asset_1 = create_market_asset('init1', precision, options=asset_1_options)
    asset_2 = create_market_asset('init2', precision, options=asset_2_options)

    log_step('Publish assets feed')
    publish_asset_feed('init1', asset_1.name, asset_1.id)
    publish_asset_feed('init2', asset_2.name, asset_2.id)
    wait_blocks()

    log_step('Borrow assets')
    CLI_WALLET.borrow_asset(
        account_1.name, amount_to_borrow, asset_1.name, '1000')
    CLI_WALLET.borrow_asset(
        account_2.name, amount_to_borrow, asset_2.name, '4000')
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Get referrers assets rewards')
    referrer_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_1.name,
                                                           asset_2.id)
    referrer_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_2.name,
                                                           asset_1.id)

    log_step('Withdraw vesting fee by referrers')
    CLI_WALLET.withdraw_vesting(referrer_1_mfs_vb.id, asset_2,
                                referrer_1_mfs_vb.asset_amount)
    CLI_WALLET.withdraw_vesting(referrer_2_mfs_vb.id, asset_1,
                                referrer_2_mfs_vb.asset_amount)
    wait_blocks()

    log_step('Check that referrers got their rewards')
    ref1_asset_2_balance = CLI_WALLET.get_asset_account_balance(
        referrer_1.name, asset_2.name)
    ref2_asset_1_balance = CLI_WALLET.get_asset_account_balance(
        referrer_2.name, asset_1.name)

    assert ref1_asset_2_balance == referrer_1_mfs_vb.asset_amount
    assert ref2_asset_1_balance == referrer_2_mfs_vb.asset_amount

    log_step('Check that referrers rewards are zero now')
    referrer_1_mfs_vb_after = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)
    referrer_2_mfs_vb_after = CLI_WALLET.get_mfs_vesting_balance(
        referrer_2.name, asset_1.id)
    assert referrer_1_mfs_vb_after.asset_amount == 0
    assert referrer_2_mfs_vb_after.asset_amount == 0


def test_check_withdraw_vesting_by_registrar(committee):
    precision = 0
    asset_1_percent = 100  # 100 means 1%
    asset_2_percent = 200  # 200 means 2%
    reward_percent = 100  # 100 means 1%
    amount_to_borrow = 10000000
    acc1_ref_percent = 10
    acc2_ref_percent = 10
    asset_1_amount = 400000
    asset_2_amount = 800000

    referrer_1 = create_account_with_balance(20000, lifetime=True)
    referrer_2 = create_account_with_balance(20000, lifetime=True)

    account_1 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_1.name,
                                            referrer_percent=acc1_ref_percent)
    account_2 = create_account_with_balance(balance=1000000,
                                            referrer=referrer_2.name,
                                            referrer_percent=acc2_ref_percent)

    log_step('Create 2 new market assets')
    asset_1_options = prepare_reward_marked_asset_options(
        asset_1_percent, reward_percent)
    asset_2_options = prepare_reward_marked_asset_options(
        asset_2_percent, reward_percent)

    asset_1 = create_market_asset('init1', precision, options=asset_1_options)
    asset_2 = create_market_asset('init2', precision, options=asset_2_options)

    log_step('Publish assets feed')
    publish_asset_feed('init1', asset_1.name, asset_1.id)
    publish_asset_feed('init2', asset_2.name, asset_2.id)
    wait_blocks()

    log_step('Borrow assets')
    CLI_WALLET.borrow_asset(
        account_1.name, amount_to_borrow, asset_1.name, '1000')
    CLI_WALLET.borrow_asset(
        account_2.name, amount_to_borrow, asset_2.name, '4000')
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Get registrars asset rewards')
    registrar_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                            asset_2.id)
    registrar_2_mfs_vb = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                            asset_1.id)

    log_step('Withdraw vesting fee by registrars')
    CLI_WALLET.withdraw_vesting(
        registrar_1_mfs_vb.id, asset_2, registrar_1_mfs_vb.asset_amount)
    CLI_WALLET.withdraw_vesting(
        registrar_2_mfs_vb.id, asset_1, registrar_2_mfs_vb.asset_amount)
    wait_blocks()

    log_step('Check that registrars got their rewards')
    reg1_asset_2_balance = CLI_WALLET.get_asset_account_balance(
        'nathan', asset_2.name)
    reg2_asset_1_balance = CLI_WALLET.get_asset_account_balance(
        'nathan', asset_1.name)

    assert reg1_asset_2_balance == registrar_1_mfs_vb.asset_amount
    assert reg2_asset_1_balance == registrar_2_mfs_vb.asset_amount

    log_step('Check that registrars rewards are zero now')
    registrar_1_mfs_vb_after = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                                  asset_2.id)
    registrar_2_mfs_vb_after = CLI_WALLET.get_mfs_vesting_balance('nathan',
                                                                  asset_1.id)
    assert registrar_1_mfs_vb_after.asset_amount == 0
    assert registrar_2_mfs_vb_after.asset_amount == 0
