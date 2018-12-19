from utils.cli_wallet import CLI_WALLET
from utils.py_logger import log_step
from utils.account import create_account_with_balance
from utils.testutil import wait_blocks
from utils.assets import (prepare_reward_user_asset_options,
                          create_new_user_asset)
from decimal import Decimal


def test_check_partial_withdraw_vesting_by_referrer(committee):
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
    asset_1_options = prepare_reward_user_asset_options(
        asset_1_percent, reward_percent)
    asset_2_options = prepare_reward_user_asset_options(
        asset_2_percent, reward_percent)

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

    log_step('Get referrer_1 mfs vesting balance')
    referrer_1_mfs_vb = CLI_WALLET.get_mfs_vesting_balance(referrer_1.name,
                                                           asset_2.id)

    log_step('Withdraw vesting half fee by referrer_1')
    half_fee = Decimal(referrer_1_mfs_vb.asset_amount) / 2
    CLI_WALLET.withdraw_vesting(referrer_1_mfs_vb.id, asset_2, half_fee)
    wait_blocks()

    log_step('Check that referrer_1 got his reward')
    ref1_asset_2_balance = CLI_WALLET.get_asset_account_balance(
        referrer_1.name, asset_2.name)
    assert Decimal(ref1_asset_2_balance) == half_fee

    log_step('Check current referrer_1 reward')
    referrer_1_mfs_vb_after = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)
    assert referrer_1_mfs_vb_after.asset_amount == half_fee

    log_step('Withdraw vesting quarter fee by referrer_1')
    quarter_fee = Decimal(half_fee) / 2
    CLI_WALLET.withdraw_vesting(referrer_1_mfs_vb_after.id, asset_2,
                                quarter_fee)
    wait_blocks()

    log_step('Check that referrer_1 got his reward')
    ref1_asset_2_balance = CLI_WALLET.get_asset_account_balance(
        referrer_1.name, asset_2.name)
    assert ref1_asset_2_balance == half_fee + quarter_fee

    log_step('Check current referrer_1 reward')
    referrer_1_mfs_vb_final = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)
    assert referrer_1_mfs_vb_final.asset_amount == quarter_fee


def test_withdraw_vesting_then_accumulation_and_withdraw_vesting_again(committee):  # noqa flake8
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
    CLI_WALLET.issue_asset(account_1.name, amount_to_issue, asset_1.name)
    CLI_WALLET.issue_asset(account_2.name, amount_to_issue, asset_2.name)
    wait_blocks()

    log_step('Sell assets')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Get referrer mfs vesting balance')
    referrer_1_mfs_vb_first = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)

    log_step('Withdraw vesting half fee by referrer')
    half_fee = Decimal(referrer_1_mfs_vb_first.asset_amount) / 2
    CLI_WALLET.withdraw_vesting(referrer_1_mfs_vb_first.id, asset_2, half_fee)
    wait_blocks()

    log_step('Sell assets again')
    CLI_WALLET.sell_asset(
        account_1.name, asset_1_amount, asset_1.name, asset_2_amount,
        asset_2.name, 300)
    CLI_WALLET.sell_asset(
        account_2.name, asset_2_amount, asset_2.name, asset_1_amount,
        asset_1.name, 300)
    wait_blocks()

    log_step('Check current referrer reward')
    referrer_1_mfs_vb_second = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)
    one_and_half_fee = half_fee + Decimal(referrer_1_mfs_vb_first.asset_amount)
    assert referrer_1_mfs_vb_second.asset_amount == one_and_half_fee

    log_step('Withdraw vesting all fee by referrers')
    CLI_WALLET.withdraw_vesting(referrer_1_mfs_vb_second.id, asset_2,
                                one_and_half_fee)
    wait_blocks()

    log_step('Check that referrers got their rewards')
    ref1_asset_2_balance = CLI_WALLET.get_asset_account_balance(
        referrer_1.name, asset_2.name)
    expected_ref1_balance = half_fee + one_and_half_fee
    assert ref1_asset_2_balance == expected_ref1_balance

    log_step('Check current referrers rewards')
    referrer_1_mfs_vb_third = CLI_WALLET.get_mfs_vesting_balance(
        referrer_1.name, asset_2.id)
    assert referrer_1_mfs_vb_third.asset_amount == 0
