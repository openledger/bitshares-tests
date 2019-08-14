import pytest
from utils.testutil import (wait_until_maintenance_finished, wait_blocks,
                            check_irreversible_block_is_updated)
from utils.account import create_account_with_balance
from utils.committee import Committee
import socket as s
from utils.cli_wallet import CLI_WALLET
from utils.py_logger import logger, PrettyFormatter
from utils.step_generator import StepGenerator
from utils.whitelist_tc_manager import WhitelistTcManager


def pytest_logger_config(logger_config):
    logger_config.add_loggers(['pytest_logger'], stdout_level='info')
    logger_config.set_log_option_default('pytest_logger')
    logger_config.set_formatter_class(PrettyFormatter)


@pytest.fixture(scope="function", autouse=True)
def reset_step_generator():
    step_generator = StepGenerator()
    step_generator.reset()


@pytest.fixture(scope="session", autouse=True)
def check_consensus():
    check_irreversible_block_is_updated()
    yield
    check_irreversible_block_is_updated()


@pytest.yield_fixture
def socket():
    _socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    yield _socket
    _socket.close()


@pytest.fixture(scope='module')
def witness_node():
    class Dummy:
        host_port = 'localhost', 12010
        uri = 'http://%s:%s/' % host_port
    return Dummy


@pytest.fixture(scope='module')
def cli_wallet():
    class Dummy:
        host_port = 'localhost', 7092
        uri = 'http://%s:%s/' % host_port
    return Dummy


@pytest.fixture
def account():
    class Dummy:
        def __init__(self):
            self.name_1 = "nathan"
            self.name_2 = "init1"
            self.name_3 = "init2"

    return Dummy()


@pytest.fixture(scope='function')
def whitelist_tc_manager():
    tc_manager = WhitelistTcManager()
    tc_manager.prepare_accounts()
    tc_manager.create_new_user_asset()
    return tc_manager


@pytest.fixture(scope="function")
def init_balances():
    CLI_WALLET.transfer("nathan", "init1", 10000)
    CLI_WALLET.transfer("nathan", "init2", 10000)


@pytest.fixture(scope="session")
def committee():
    # create new accont (testAccount)
    # transfer to testAccount BTS
    # transfer to commitee BTS from testAccount balance
    # transfer to commitee members BTS from testAccount balance
    # testAccount vote for commitee members

    logger.info('Committee fixture setup started')
    account = create_account_with_balance(5000000, referrer_percent='1')

    committee_accounts = ("init0", "init1", "init2")

    committee = Committee()

    # there are 5 operations (interval, referral_percent, subscription_plan x3)
    # that should be applied
    # it costs committee 5 tokens to make voting effective
    committee.increaseBalance(account.name, 5)

    for member in committee_accounts:
        CLI_WALLET.transfer(account.name, member, 1000000)
    wait_blocks(1)

    for member in committee_accounts:
        committee.addMember(account.name, member)

    wait_until_maintenance_finished()

    previous_global_params = CLI_WALLET.get_global_parameters()

    logger.info('Committee fixture setup finished')
    yield committee

    logger.info('Committee fixture tearDown started')
    current_global_params = CLI_WALLET.get_global_parameters()
    param_value = dict()
    for key in previous_global_params.keys():
        if isinstance(previous_global_params[key], int):
            if current_global_params[key] != previous_global_params[key]:
                param_value[key] = current_global_params[key]
                logger.info(
                    'current %s:%s' % (key, current_global_params[key]))
                logger.info(
                    'previous %s:%s' % (key, previous_global_params[key]))
                committee.update_global_property("init0", "init1", key,
                                                 previous_global_params[key])

    for member in committee_accounts:
        committee.deleteMember(account.name, member)
    wait_blocks(1)

    wait_until_maintenance_finished()
    if param_value:
        param = param_value.keys()[0]
        logger.info('Check that %s was changed back' % param)
        current_global_params = CLI_WALLET.get_global_parameters()
        assert current_global_params[param] == previous_global_params[param]
    logger.info('Committee fixture tearDown finished')


def pytest_addoption(parser):
    parser.addoption("--docker_dir", action="store", default="docker_logs")
    parser.addoption("--issuers_pairs_count", action="store", default=2)
    parser.addoption("--issuer_assets_count", action="store", default=10)
    parser.addoption("--sellers_count", action="store", default=100)
    parser.addoption("--holders_count", action="store", default=100)
    parser.addoption("--with_fba", action="store", default=False)
    parser.addoption("--csv_file_name", action="store",
                     default='performance_results.csv')
    parser.addoption("--new_maintenance", action="store", default=10)
    parser.addoption("--bts_for_issuers", action="store", default=1000000)
    parser.addoption("--ordinary_accounts_count", action="store",
                     default=100000)


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".

    option_docker_dir = metafunc.config.option.docker_dir
    if 'docker_dir' in metafunc.fixturenames and option_docker_dir is not None:
        metafunc.parametrize("docker_dir", [option_docker_dir])

    option_issuers_pairs_count = metafunc.config.option.issuers_pairs_count
    if 'issuers_pairs_count' in metafunc.fixturenames and \
            option_issuers_pairs_count is not None:
        metafunc.parametrize(
            "issuers_pairs_count", [option_issuers_pairs_count])

    option_issuer_assets_count = metafunc.config.option.issuer_assets_count
    if 'issuer_assets_count' in metafunc.fixturenames and \
            option_issuer_assets_count is not None:
        metafunc.parametrize(
            "issuer_assets_count", [option_issuer_assets_count])

    option_sellers_count = metafunc.config.option.sellers_count
    if 'sellers_count' in metafunc.fixturenames and \
            option_sellers_count is not None:
        metafunc.parametrize("sellers_count", [option_sellers_count])

    option_holders_count = metafunc.config.option.holders_count
    if 'holders_count' in metafunc.fixturenames and \
            option_holders_count is not None:
        metafunc.parametrize("holders_count", [option_holders_count])

    option_with_fba = metafunc.config.option.with_fba
    if 'with_fba' in metafunc.fixturenames and option_with_fba is not None:
        metafunc.parametrize("with_fba", [option_with_fba])

    option_csv_file_name = metafunc.config.option.csv_file_name
    if 'csv_file_name' in metafunc.fixturenames and \
            option_csv_file_name is not None:
        metafunc.parametrize("csv_file_name", [option_csv_file_name])

    option_new_maintenance = metafunc.config.option.new_maintenance
    if 'new_maintenance' in metafunc.fixturenames and \
            option_new_maintenance is not None:
        metafunc.parametrize("new_maintenance", [option_new_maintenance])

    option_bts_for_issuers = metafunc.config.option.bts_for_issuers
    if 'bts_for_issuers' in metafunc.fixturenames and \
            option_bts_for_issuers is not None:
        metafunc.parametrize("bts_for_issuers", [option_bts_for_issuers])

    option_ordinary_accounts_count = \
        metafunc.config.option.ordinary_accounts_count
    if 'ordinary_accounts_count' in metafunc.fixturenames and \
            option_ordinary_accounts_count is not None:
        metafunc.parametrize("ordinary_accounts_count",
                             [option_ordinary_accounts_count])
