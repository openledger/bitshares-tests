from utils.cli_wallet import CLI_WALLET
from utils.py_logger import log_step
from utils.testutil import calculate_full_reward_amount


def test_add_registrar_to_whitelist_so_registrar_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2]
    Asset Blacklist: []
    MFS Whitelist: []
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Get mfs vesting balances list of registrar_2')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)

    log_step('Calculate expected registrar2 reward (It is full reward amount)')
    expected_registrar_2_reward = calculate_full_reward_amount(
        whitelist_tc_manager.asset_1, whitelist_tc_manager.asset_1_amount,
        whitelist_tc_manager.asset_1_percent,
        whitelist_tc_manager.reward_percent)

    log_step('Check mfs vesting balances of registrar_2 is correct')
    asset_1_dict = {'asset_id': whitelist_tc_manager.asset_1.id,
                    'amount': expected_registrar_2_reward}

    assert len(registrar_2_list_rewards) == 1

    mfs_vesting_balance = registrar_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_registrar_to_whitelist_and_to_mfs_witelist_so_registrar_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2]
    Asset Blacklist: []
    MFS Whitelist: [Registrar_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)

    mfs_whitelist = [whitelist_tc_manager.registrar_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Get mfs vesting balances list of registrar_2')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)

    log_step('Calculate expected registrar2 reward (It is full reward amount)')
    expected_registrar_2_reward = calculate_full_reward_amount(
        whitelist_tc_manager.asset_1, whitelist_tc_manager.asset_1_amount,
        whitelist_tc_manager.asset_1_percent,
        whitelist_tc_manager.reward_percent)

    log_step('Check mfs vesting balances of registrar_2 is correct')
    asset_1_dict = {'asset_id': whitelist_tc_manager.asset_1.id,
                    'amount': expected_registrar_2_reward}

    assert len(registrar_2_list_rewards) == 1

    mfs_vesting_balance = registrar_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_registrar_to_whitelist_and_referrer_to_mfs_whitelist_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2]
    Asset Blacklist: []
    MFS Whitelist: [Referrer_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)

    mfs_whitelist = [whitelist_tc_manager.referrer_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_registrar_to_whitelist_and_registrar_and_referrer_to_mfs_whitelist_so_only_registrar_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2]
    Asset Blacklist: []
    MFS Whitelist: [Registrar_2, Referrer_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)

    log_step('Update MFS whitelist')
    mfs_whitelist = [
        whitelist_tc_manager.registrar_2.id,
        whitelist_tc_manager.referrer_2.id
    ]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Get mfs vesting balances list of registrar_2')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)

    log_step('Calculate expected registrar2 reward (It is full reward amount)')
    expected_registrar_2_reward = calculate_full_reward_amount(
        whitelist_tc_manager.asset_1, whitelist_tc_manager.asset_1_amount,
        whitelist_tc_manager.asset_1_percent,
        whitelist_tc_manager.reward_percent)

    log_step('Check mfs vesting balances of registrar_2 is correct')
    asset_1_dict = {'asset_id': whitelist_tc_manager.asset_1.id,
                    'amount': expected_registrar_2_reward}

    assert len(registrar_2_list_rewards) == 1

    mfs_vesting_balance = registrar_2_list_rewards[0]
    assert mfs_vesting_balance.allowed_withdraw == asset_1_dict

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_referrer_to_whitelist_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: []
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_referrer_to_whitelist_and_registrar_to_mfs_whitelist_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: [Registrar_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    log_step('Update MFS whitelist')
    mfs_whitelist = [whitelist_tc_manager.registrar_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_referrer_to_whitelist_and_referrer_to_mfs_whitelist_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: [Referrer_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    log_step('Update MFS whitelist')
    mfs_whitelist = [whitelist_tc_manager.registrar_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_referrer_to_whitelist_and_registrar_and_referrer_to_mfs_whitelist_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: [Registrar_2, Referrer_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    log_step('Update MFS whitelist')
    mfs_whitelist = [
        whitelist_tc_manager.registrar_2.id,
        whitelist_tc_manager.referrer_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_registrar_and_referrer_to_whitelist_so_all_of_them_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: []
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has reward')
    whitelist_tc_manager.check_if_reward_amount_is_correct(
        whitelist_tc_manager.registrar_2.name,
        whitelist_tc_manager.reg_2_percent)

    log_step('Check that referrer_2 has reward')
    whitelist_tc_manager.check_if_reward_amount_is_correct(
        whitelist_tc_manager.referrer_2.name,
        whitelist_tc_manager.ref_2_percent)


def test_add_registrar_and_referrer_to_whitelist_and_registrar_to_mfs_whitelist_so_all_of_them_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: [Registrar_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    log_step('Update MFS whitelist')
    mfs_whitelist = [whitelist_tc_manager.registrar_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has reward')
    whitelist_tc_manager.check_if_reward_amount_is_correct(
        whitelist_tc_manager.registrar_2.name,
        whitelist_tc_manager.reg_2_percent)

    log_step('Check that referrer_2 has reward')
    whitelist_tc_manager.check_if_reward_amount_is_correct(
        whitelist_tc_manager.referrer_2.name,
        whitelist_tc_manager.ref_2_percent)


def test_add_registrar_and_referrer_to_whitelist_and_referrer_to_mfs_whitelist_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: [Referrer_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    log_step('Update MFS whitelist')
    mfs_whitelist = [whitelist_tc_manager.referrer_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_add_registrar_and_referrer_to_whitelist_and_to_mfs_whitelist_so_all_of_them_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2, Registrar_2, Referrer_2]
    Asset Blacklist: []
    MFS Whitelist: [Registrar_2, Referrer_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.registrar_2.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.referrer_2.name)

    log_step('Update MFS whitelist')
    mfs_whitelist = [whitelist_tc_manager.registrar_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has reward')
    whitelist_tc_manager.check_if_reward_amount_is_correct(
        whitelist_tc_manager.registrar_2.name,
        whitelist_tc_manager.reg_2_percent)

    log_step('Check that referrer_2 has reward')
    whitelist_tc_manager.check_if_reward_amount_is_correct(
        whitelist_tc_manager.referrer_2.name,
        whitelist_tc_manager.ref_2_percent)


def test_only_sellers_are_in_whitelist_and_mfs_whitelist_is_empty_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2]
    Asset Blacklist: []
    MFS Whitelist: []
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)

    mfs_whitelist = [whitelist_tc_manager.referrer_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []


def test_only_sellers_are_in_whitelist_and_registrar_and_referrer_are_in_mfs_whitelist_so_no_one_can_get_reward(whitelist_tc_manager):  # noqa flake8
    """
    Asset Whitelist: [Account_1, Account_2]
    Asset Blacklist: []
    MFS Whitelist: [Registrar_2, Referrer_2]
    """
    # Creation of registrar, referrer, accounts and new user asset have
    # been executed in "whitelist_tc_manager" fixture

    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_1.name)
    whitelist_tc_manager.set_whitelist(whitelist_tc_manager.account_2.name)

    mfs_whitelist = [whitelist_tc_manager.registrar_2.id,
                     whitelist_tc_manager.referrer_2.id]
    whitelist_tc_manager.update_mfs_whitelist(mfs_whitelist)

    whitelist_tc_manager.issue_and_sell_assets()

    log_step('Check that registrar_2 has no any reward')
    registrar_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.registrar_2.name)
    assert registrar_2_list_rewards == []

    log_step('Check that referrer_2 has no any reward')
    referrer_2_list_rewards = CLI_WALLET.get_mfs_vesting_balances_list(
        whitelist_tc_manager.referrer_2.name)
    assert referrer_2_list_rewards == []
