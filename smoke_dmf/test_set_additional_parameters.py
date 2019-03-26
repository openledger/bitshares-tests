import pytest
from utils.py_logger import log_step
from utils.account import create_account_with_balance
from utils.dmf_asset import (create_dmf_asset, prepare_dmf_asset_options,
                             DMFAsset)
from utils.user_asset import create_user_asset
from utils.constants import DEFAULT_EXTENSIONS, DMF_ASSET_FLAG
from copy import deepcopy
from utils.testutil import generate_new_asset_name


def test_create_dynamic_market_fee_asset():

    dmf_asset_flag = 512
    extensions = {
        "dynamic_fees": {
            "maker_fee": [{"amount": 0, "percent": 2500},
                          {"amount": 1000, "percent": 2000}],
            "taker_fee": [{"amount": 0, "percent": 1000},
                          {"amount": 2000, "percent": 500}]
        }
    }

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Create dmf asset')
    dmf_name = generate_new_asset_name()
    options = prepare_dmf_asset_options(extensions, dmf_asset_flag)

    dmf_asset = DMFAsset(account_1.name, 1, dmf_name)
    dmf_asset.create_asset(options)

    log_step('Check options')
    current_options = dmf_asset.get_options()
    assert current_options['extensions'] == extensions
    assert current_options['flags'] == dmf_asset_flag


@pytest.mark.parametrize('incorrect_flag', [256, 0])
def test_try_to_create_dmf_asset_with_wrong_flag(incorrect_flag):

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Try to create DMF asset with "%s" flag' % incorrect_flag)
    dmf_asset = DMFAsset(account_1.name)

    options = prepare_dmf_asset_options(DEFAULT_EXTENSIONS,
                                        flags_int=incorrect_flag)
    response = dmf_asset.try_create_asset(options)

    log_step('Check expected error message')
    expected_error_message = 'Dynamic market fee table and ' \
                             'charge_dynamic_market_fee should be used in ' \
                             'together'
    assert expected_error_message in response['error']['message']


def test_try_to_create_dmf_asset_with_empty_table():

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Prepare options with wrong flag')
    dmf_asset = DMFAsset(account_1.name)

    cases = (
        {},
        {
            "maker_fee": [{"amount": 0, "percent": 2500}]
        },
        {
            "taker_fee": [{"amount": 0, "percent": 1000}]
        },
        {
            "maker_fee": [{"amount": 0, "percent": 2500}],
            "taker_fee": []
        },
        {
            "maker_fee": [],
            "taker_fee": [{"amount": 0, "percent": 1000}]
        },
    )

    for case in cases:
        extensions = {'dynamic_fees': case}

        log_step('Try to create DMF asset with "%s" extensions' % extensions)
        options = prepare_dmf_asset_options(extensions,
                                            flags_int=DMF_ASSET_FLAG)
        response = dmf_asset.try_create_asset(options)

        log_step('Check expected error message')
        expected_error_message = 'Dynamic market fee (maker or taker) table ' \
                                 'should be non empty'
        assert expected_error_message in response['error']['message']


@pytest.mark.parametrize('trader', ['maker', 'taker'])
def test_try_to_create_dmf_asset_with_only_non_zero_amount_in_table(trader):

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Prepare options with non zero amount in table')
    dmf_asset = DMFAsset(account_1.name)

    cases = (-1, 1, 100)

    for case in cases:
        maker_fee_amount = case if trader == 'maker' else 0
        taker_fee_amount = case if trader == 'taker' else 0

        extensions = {'dynamic_fees': {
            "maker_fee": [{"amount": maker_fee_amount, "percent": 2500}],
            "taker_fee": [{"amount": taker_fee_amount, "percent": 1000}]
        }}

        log_step('Try to create DMF asset with "%s" extensions' % extensions)
        options = prepare_dmf_asset_options(extensions)
        response = dmf_asset.try_create_asset(options)

        log_step('Check expected error message')
        expected_error_message = 'Dynamic market fee %s amount should start ' \
                                 'from zero' % trader
        assert expected_error_message in response['error']['message']


@pytest.mark.parametrize('trader', ['maker', 'taker'])
def test_try_to_create_dmf_asset_with_incorrect_fee_percent_in_table(trader):

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Prepare options with non zero amount in table')
    dmf_asset = DMFAsset(account_1.name)

    cases = (-100, -1, 10001)

    for case in cases:
        maker_fee_percent = case if trader == 'maker' else 10000
        taker_fee_percent = case if trader == 'taker' else 10000

        extensions = {'dynamic_fees': {
            "maker_fee": [{"amount": 0, "percent": maker_fee_percent}],
            "taker_fee": [{"amount": 0, "percent": taker_fee_percent}]
        }}

        log_step('Try to create DMF asset with "%s" extensions' % extensions)
        options = prepare_dmf_asset_options(extensions, DMF_ASSET_FLAG)
        response = dmf_asset.try_create_asset(options)

        log_step('Check expected error message')
        expected_error_message = '%s percent should be in range [0 - 10000]' %\
                                 trader.title()
        assert expected_error_message in response['error']['message']


@pytest.mark.parametrize('trader_fee', ['maker_fee', 'taker_fee'])
def test_try_to_create_dmf_asset_with_duplicated_fee_amount_in_table(trader_fee):  # noqa flake8

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Prepare options with non zero amount in table')
    dmf_asset = DMFAsset(account_1.name)

    extensions = {'dynamic_fees': {
        "maker_fee": [{"amount": 0, "percent": 1000}],
        "taker_fee": [{"amount": 0, "percent": 1000}]
    }}

    extensions['dynamic_fees'][trader_fee].append({"amount": 0,
                                                   "percent": 2000})

    log_step('Create DMF asset with "%s" extensions' % extensions)
    options = prepare_dmf_asset_options(extensions, DMF_ASSET_FLAG)
    dmf_asset.create_asset(options)

    log_step('Check current options')
    del extensions['dynamic_fees'][trader_fee][1]
    assert dmf_asset.get_options()['extensions'] == extensions


def test_create_dmf_asset_when_zero_amount_is_not_in_first_position_in_table():

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Prepare options with non zero amount in table')
    dmf_asset = DMFAsset(account_1.name)

    extensions = {'dynamic_fees': {
        "maker_fee": [{"amount": 100, "percent": 1000},
                      {"amount": 200, "percent": 2000},
                      {"amount": 0, "percent": 3000}],
        "taker_fee": [{"amount": 100, "percent": 1000},
                      {"amount": 200, "percent": 2000},
                      {"amount": 0, "percent": 3000}]
    }}

    log_step('Create DMF asset with "%s" extensions' % extensions)
    options = prepare_dmf_asset_options(extensions, DMF_ASSET_FLAG)
    dmf_asset.create_asset(options)

    log_step('Sort prepared extensions')
    extensions['dynamic_fees']['maker_fee'].sort()
    extensions['dynamic_fees']['taker_fee'].sort()

    log_step('Check current options')
    assert dmf_asset.get_options()['extensions'] == extensions


def test_update_dmf_asset_to_user_asset():

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, 100000)

    log_step('Update DMF asset to user asset')
    current_options = dmf_asset.get_options()
    new_options = deepcopy(current_options)

    new_options['flags'] = 0
    del new_options['extensions']

    dmf_asset.update_options(new_options)

    log_step('Check that asset is not dmf')
    final_options = dmf_asset.get_options()
    assert final_options['extensions'] == {}

    del final_options['extensions']
    assert final_options == new_options


def test_change_only_flag_and_try_to_update_dmf_asset_to_user_asset():
    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, 100000)

    log_step('Try to update DMF asset to user asset')
    current_options = dmf_asset.get_options()
    new_options = deepcopy(current_options)

    new_options['flags'] = 0

    response = dmf_asset.try_update_options(new_options)

    log_step('Check expected error message')
    expected_error_message = 'Dynamic market fee table and ' \
                             'charge_dynamic_market_fee should be used in ' \
                             'together'
    assert expected_error_message in response['error']['message']


def test_remove_only_fee_table_and_try_to_update_dmf_asset_to_user_asset():
    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Create dmf asset')
    dmf_asset = create_dmf_asset(account_1.name, 100000)

    log_step('Remove "extensions" and try to update DMF asset to user asset')
    current_options = dmf_asset.get_options()
    new_options = deepcopy(current_options)

    del new_options['extensions']

    response = dmf_asset.try_update_options(new_options)

    log_step('Check expected error message')
    expected_error_message = 'Dynamic market fee table and ' \
                             'charge_dynamic_market_fee should be used in ' \
                             'together'
    assert expected_error_message in response['error']['message']


def test_update_user_asset_to_dmf_asset():

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Create user asset')
    user_asset = create_user_asset(account_1.name, 10000, 1,
                                   permissions_int=DMF_ASSET_FLAG)

    log_step('Update user asset to DMF asset')
    current_options = user_asset.get_options()
    new_options = deepcopy(current_options)

    new_options['flags'] = DMF_ASSET_FLAG
    new_options['extensions'] = DEFAULT_EXTENSIONS

    user_asset.update_options(new_options)

    log_step('Check that asset is dmf')
    final_options = user_asset.get_options()
    assert final_options == new_options


def test_try_to_update_user_asset_with_zero_permissions_int_to_dmf_asset():

    log_step('Create new account')
    account_1 = create_account_with_balance(10000)

    log_step('Create user asset')
    user_asset = create_user_asset(account_1.name, 10000, 1,
                                   permissions_int=0)

    log_step('Try to update user asset to DMF asset')
    current_options = user_asset.get_options()
    new_options = deepcopy(current_options)

    new_options['flags'] = DMF_ASSET_FLAG
    new_options['extensions'] = DEFAULT_EXTENSIONS

    response = user_asset.try_update_options(new_options)

    log_step('Check expected error message')
    expected_error_message = 'Flag change is forbidden by issuer permissions'
    assert expected_error_message in response['error']['message']
