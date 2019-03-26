import pytest
from utils.py_logger import log_step
from utils.account import create_account_with_balance
from utils.dmf_asset import (create_dmf_asset, prepare_dmf_asset_options,
                             DMFAsset)
from utils.constants import DEFAULT_CORE_ASSET
from utils.testutil import calculate_percent, generate_new_asset_name


@pytest.mark.parametrize('taker_fee_percent', [0, 1, 9999, 10000])
def test_set_boundary_percent_then_trade_dmf_and_check_taker_balance(taker_fee_percent):  # noqa flake8

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 10000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": 1000}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Calculate expected taker balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               taker_fee_percent)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check taker balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


@pytest.mark.parametrize('maker_fee_percent', [0, 1, 9999, 10000])
def test_set_boundary_percent_then_trade_dmf_and_check_maker_balance(maker_fee_percent):  # noqa flake8

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 10000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": maker_fee_percent}],
            "taker_fee": [{"amount": 0, "percent": 1000}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts')
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)

    log_step('Calculate expected maker balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               maker_fee_percent)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check taker balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


def test_amount_to_sell_is_more_than_first_border_value_so_check_that_applied_fee_is_correct():  # noqa flake8

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 1000

    taker_fee_percent_1 = 2000
    taker_fee_percent_2 = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": 500}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent_1},
                          {"amount": 999, "percent": taker_fee_percent_2}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Calculate expected taker balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               taker_fee_percent_1)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check taker balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


def test_update_taker_trade_statistics_and_check_that_applied_fee_is_correct():

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 1000

    taker_fee_percent_1 = 2000
    taker_fee_percent_2 = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": 500}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent_1},
                          {"amount": 1000, "percent": taker_fee_percent_2}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Transfer dmf asset so account has zero balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    account_2.transfer(account_1.name, account_2_balance, dmf_asset.name)

    log_step('Sell assets between accounts one more time')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Calculate expected account balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               taker_fee_percent_2)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check account balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


def test_update_maker_trade_statistics_and_check_that_applied_fee_is_correct():

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 1000

    maker_fee_percent_1 = 2000
    maker_fee_percent_2 = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": maker_fee_percent_1},
                          {"amount": 1000, "percent": maker_fee_percent_2}],
            "taker_fee": [{"amount": 0, "percent": 500}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts')
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)

    log_step('Transfer dmf asset so account has zero balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    account_2.transfer(account_1.name, account_2_balance, dmf_asset.name)

    log_step('Sell assets between accounts one more time')
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)

    log_step('Calculate expected account balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               maker_fee_percent_2)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check account balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


def test_update_trade_statistics_as_taker_then_use_it_as_maker():

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 1000

    maker_fee_percent_1 = 500
    maker_fee_percent_2 = 100

    taker_fee_percent_1 = 2000
    taker_fee_percent_2 = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": maker_fee_percent_1},
                          {"amount": 1000, "percent": maker_fee_percent_2}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent_1},
                          {"amount": 1000, "percent": taker_fee_percent_2}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts. Trade as taker')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Transfer dmf asset so account has zero balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    account_2.transfer(account_1.name, account_2_balance, dmf_asset.name)

    log_step('Sell assets between accounts one more time. Trade as maker')
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)

    log_step('Calculate expected account balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               maker_fee_percent_2)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check account balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


def test_update_trade_statistics_as_maker_then_use_it_as_taker():

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 1000

    maker_fee_percent_1 = 500
    maker_fee_percent_2 = 100

    taker_fee_percent_1 = 2000
    taker_fee_percent_2 = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": maker_fee_percent_1},
                          {"amount": 1000, "percent": maker_fee_percent_2}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent_1},
                          {"amount": 1000, "percent": taker_fee_percent_2}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts. Trade as maker')
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)

    log_step('Transfer dmf asset so account has zero balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    account_2.transfer(account_1.name, account_2_balance, dmf_asset.name)

    log_step('Sell assets between accounts one more time. Trade as taker')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Calculate expected account balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               taker_fee_percent_2)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check account balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


def test_max_market_fee_with_dmf_asset_for_maker():

    amount_to_issue = 10000
    amount_to_sell = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    max_market_fee = 400
    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": 9000}],
            "taker_fee": [{"amount": 0, "percent": 100}]
        }
    }

    log_step('Create dmf asset')
    dmf_name = generate_new_asset_name()
    options = prepare_dmf_asset_options(extensions,
                                        max_market_fee=max_market_fee)
    dmf_asset = DMFAsset(account_1.name, 0, dmf_name)
    dmf_asset.create_asset(options)
    dmf_asset.issue_asset(amount_to_issue)

    log_step('Sell assets between accounts')
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)

    log_step('Get account dmf balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)

    log_step('Check account dmf balance')
    expected_account_2_balance = amount_to_sell - max_market_fee
    assert account_2_balance == expected_account_2_balance


def test_max_market_fee_with_dmf_asset_for_taker():

    amount_to_issue = 10000
    amount_to_sell = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    max_market_fee = 400
    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": 100}],
            "taker_fee": [{"amount": 0, "percent": 9000}]
        }
    }

    log_step('Create dmf asset')
    dmf_name = generate_new_asset_name()
    options = prepare_dmf_asset_options(extensions,
                                        max_market_fee=max_market_fee)
    dmf_asset = DMFAsset(account_1.name, 0, dmf_name)
    dmf_asset.create_asset(options)
    dmf_asset.issue_asset(amount_to_issue)

    log_step('Sell assets between accounts')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Get account dmf balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)

    log_step('Check account balance')
    expected_account_2_balance = amount_to_sell - max_market_fee
    assert account_2_balance == expected_account_2_balance


def test_update_dmf_asset_table_then_check_applied_fee():

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 10000
    amount_to_sell = 1000

    taker_fee_percent_1 = 1000
    taker_fee_percent_2 = 500

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": 100}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent_1},
                          {"amount": 5000, "percent": taker_fee_percent_2}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Update dmf asset')
    extensions['dynamic_fees']['taker_fee'][1]['amount'] = 1000
    current_options = dmf_asset.get_options()
    current_options['extensions'] = extensions
    dmf_asset.update_options(current_options)

    log_step('Transfer dmf asset so account has zero balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    account_2.transfer(account_1.name, account_2_balance, dmf_asset.name)

    log_step('Sell assets between accounts one more time')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Calculate expected account balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               taker_fee_percent_2)
    expected_account_2_balance = amount_to_sell - expected_account_2_fee

    log_step('Check account balance')
    account_2_balance = account_2.get_asset_account_balance(dmf_asset.name)
    assert account_2_balance == expected_account_2_balance


def test_trade_dmf_asset_and_check_if_accumulated_fees_are_correct():

    precision = 0
    precision_value = 10 ** precision

    amount_to_issue = 100000
    amount_to_sell = 1000

    maker_fee_percent = 2000
    taker_fee_percent = 1000

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)
    account_2 = create_account_with_balance(20000)

    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": maker_fee_percent}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent}]
        }
    }

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, amount_to_issue,
                                 precision=precision, extensions=extensions)

    log_step('Sell assets between accounts')
    account_1.sell_asset(amount_to_sell, dmf_asset.name, amount_to_sell,
                         DEFAULT_CORE_ASSET)
    account_2.sell_asset(amount_to_sell, DEFAULT_CORE_ASSET, amount_to_sell,
                         dmf_asset.name)

    log_step('Calculate expected account balance')
    expected_account_2_fee = calculate_percent(amount_to_sell*precision_value,
                                               taker_fee_percent)

    log_step('Check accumulated fees')
    accumulated_fees = dmf_asset.get_accumulated_fees()
    assert accumulated_fees == expected_account_2_fee
