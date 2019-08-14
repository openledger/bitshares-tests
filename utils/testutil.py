import random
import string
import time
from datetime import datetime, timedelta
import dateutil.parser as dt
from utils.cli_wallet import CLI_WALLET
from utils.py_logger import logger
import re
import os
from utils.constants import DMF_ASSET_FLAG


def get_last_operation_id(account_name):
    account = CLI_WALLET.get_account(account_name)
    stats = CLI_WALLET.get_object(account["statistics"])
    most_recent_op = CLI_WALLET.get_object(stats[0]["most_recent_op"])
    return most_recent_op[0]["operation_id"]


def get_last_operation(account):
    operation = CLI_WALLET.get_object(get_last_operation_id(account))
    return operation[0]


def get_timestamp():
    now = datetime.now()
    return str(int(now.strftime("%s")) * 1000)


def date_from_string(datestr):
    return dt.parse(datestr)


def date_from_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp)


def generate_random_string(length):
    return ''.join(random.choice(string.lowercase) for _ in range(length))


def generate_random_key():
    ts = get_timestamp()
    key = ts + generate_random_string(10)
    return key


def generate_random_name():
    ts = get_timestamp()
    name = generate_random_string(10) + ts
    return name


def wait_until_maintenance_finished():
    next_maintenance_time = CLI_WALLET.get_next_maintenance_time()
    while True:
        prop = CLI_WALLET.get_dynamic_global_properties()
        now = dt.parse(prop["time"])

        if now < next_maintenance_time:
            time.sleep(1)
        else:
            break
    return next_maintenance_time


def wait_for_maintenance_after(timestamp):
    while True:
        prop = CLI_WALLET.get_dynamic_global_properties()
        now = dt.parse(prop["time"])
        next_maintenance_time = dt.parse(prop["next_maintenance_time"])

        if now < timestamp:
            time.sleep(0.5)
        else:
            if timestamp < next_maintenance_time:
                timestamp = next_maintenance_time
            break
    wait_until(timestamp)
    return timestamp


def wait_blocks(num_blocks=1):
    logger.info('Waiting for new block is generated')
    block = CLI_WALLET.get_head_block_number()
    while CLI_WALLET.get_head_block_number() - block < num_blocks:
        sleep_time = 0.5
        logger.debug('Sleep %s seconds' % sleep_time)
        time.sleep(sleep_time)
    logger.info('Done.')


def wait_until(timestamp):
    logger.info('Wait until %s...' % timestamp)
    while timestamp > dt.parse(
            CLI_WALLET.get_dynamic_global_properties()["time"]):
        time.sleep(1)


def wait_proposal_processed(proposal_id):
    result = CLI_WALLET.get_object(proposal_id)[0]
    if result is not None:
        expiration_time = dt.parse(result["expiration_time"])
        wait_until(expiration_time)
        wait_blocks(2)


def wait_operation_processed(account, operation_id):
    while operation_id == get_last_operation_id(account):
        time.sleep(1)


def update_timestamp(timestamp, minutes=0, seconds=0):
    timestamp = prepare_datetime_object(timestamp)
    new_timestamp = timestamp + timedelta(minutes=minutes, seconds=seconds)
    return new_timestamp


def prepare_datetime_object(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp
    else:
        return dt.parse(timestamp)


def calculate_trade_statistics(start_amount, first_maintenance_time,
                               extra_timestamp=None):
    maintenance_interval = CLI_WALLET.get_maintenance_interval()
    extra_timestamp = first_maintenance_time if extra_timestamp is None \
        else extra_timestamp
    delta = extra_timestamp - first_maintenance_time
    first_maintenance_count = 1
    extra_maintenance_count = delta.seconds / maintenance_interval
    all_maintenance_count = first_maintenance_count + extra_maintenance_count

    for _ in xrange(all_maintenance_count):
        start_amount = trade_statistics_calculator(start_amount)
    return start_amount


def trade_statistics_calculator(start_amount):
    start_amount = 59 * start_amount / 60
    return start_amount


def choose_new_block_interval():
    current = CLI_WALLET.get_block_interval()
    maint_interval = CLI_WALLET.get_maintenance_interval()

    for i in range(1, maint_interval):
        if 0 == maint_interval % i and i != current:
            return i

    raise AssertionError()


def choose_new_gas_price():
    current_gas_price = CLI_WALLET.get_gas_price()
    while True:
        new_gas_price = random.randint(1, 10)
        if new_gas_price != current_gas_price:
            return new_gas_price


def choose_new_gas_limit():
    current_gas_limit = CLI_WALLET.get_gas_limit()
    while True:
        new_gas_limit = random.randint(1, 1000000)
        if new_gas_limit != current_gas_limit:
            return new_gas_limit


def prepare_market_asset_options(permissions, flags):
    # TODO see http://docs.bitshares.org/bitshares/tutorials/uia-create-manual.html # noqa flake8
    perm = dict()
    perm["charge_market_fee"] = 0x01
    perm["white_list"] = 0x02
    perm["override_authority"] = 0x04
    perm["transfer_restricted"] = 0x08
    perm["disable_force_settle"] = 0x10
    perm["global_settle"] = 0x20
    perm["disable_confidential"] = 0x40
    perm["witness_fed_asset"] = 0x80
    perm["committee_fed_asset"] = 0x100

    permissions_int = 0
    for p in permissions:
        if permissions[p]:
            permissions_int += perm[p]
    flags_int = 0
    for p in permissions:
        if flags[p]:
            flags_int += perm[p]

    return prepare_asset_options(permissions_int, flags_int)


def prepare_asset_options(permissions_int, flags_int):
    options = {"max_supply": 100000,
               "market_fee_percent": 0,
               "max_market_fee": 0,
               "issuer_permissions": permissions_int,
               "flags": flags_int,
               "core_exchange_rate": {
                   "base": {
                       "amount": 10,
                       "asset_id": "1.3.0"},
                   "quote": {
                       "amount": 10,
                       "asset_id": "1.3.1"}},
               "whitelist_authorities": [],
               "blacklist_authorities": [],
               "whitelist_markets": [],
               "blacklist_markets": [],
               "description": "Test asset description"
               }
    return options


def asset_exists(asset_symbol_or_id):
    response = CLI_WALLET.try_send_request("get_asset", [asset_symbol_or_id])
    return 'result' in response


def get_expiration_time(lifetime_seconds):
    now = dt.parse(CLI_WALLET.get_dynamic_global_properties()["time"])
    expiration = now + timedelta(seconds=lifetime_seconds)
    expiration_iso = expiration.replace(microsecond=0).isoformat()
    return expiration_iso


def get_first_amount(account):
    try:
        amount = int(CLI_WALLET.get_account_balance(account)[0]['amount'])
    except IndexError:
        amount = 0
    return amount


def wait_transfer(from_account, to_account, amount):
    prev = get_first_amount(to_account)
    CLI_WALLET.transfer(from_account, to_account, amount)

    while get_first_amount(to_account) - prev < amount:
        time.sleep(1)


def check_committee_preconditions(committee):
    # pre-condition 1: the committee member must be voted in (init0,
    # init1 and init3)
    # precondition 2: 1 < get_maintenance_interval()
    # precondition 3: the committee account should not have empty balance
    assert 3 == len(committee.members())
    assert 1 < CLI_WALLET.get_maintenance_interval()


def calculate_percent(value, percent, bitshares_value=True):
    percent = float(percent) / float(100) if bitshares_value else percent
    result = value * percent / 100
    return result


def percentage(part, whole):
    return int(100 * float(part) / float(whole))


def generate_new_asset_name(symbol_length=7):
    assert symbol_length <= 16, 'Symbol length more than 16'
    symbol_length -= 1
    while True:
        asset_name = generate_random_string(symbol_length).upper()
        asset_name = 'A%s' % asset_name
        if not asset_exists(asset_name):
            return asset_name


def seller_list_generator(even_list, odd_list):
    assert len(even_list) == len(odd_list), 'Lists length should be the same'
    for list_index in range(len(even_list)):
        yield even_list[list_index], odd_list[list_index]


def get_file_lines(file_path):
    with open(file_path, 'rb') as opened_file:
        return opened_file.readlines()


def get_block_number_from_log_line(line):
    result = re.findall('#\d*', line)
    # Example of result: ['#1234']
    return result[0][1:]


def get_time_from_line(line):
    result = line.split()[0]
    # Example of result: '1234000ms'
    return result[:-2]


def calculate_maintenance_time(start, finish):
    assert start is not None
    assert finish is not None
    time_in_ms = int(finish) - int(start)
    return time_in_ms


def check_maintenance_time(docker_dir, block_before_maintenance):
    logger.info('Searching for next maintenance block...')
    start_time = None
    finish_time = None
    maintenance_block = None
    log_file_path = os.path.join(docker_dir, 'log')
    file_lines = get_file_lines(log_file_path)
    for line in file_lines:
        if 'Started in block=#' in line:
            block = get_block_number_from_log_line(line)
            if int(block) > int(block_before_maintenance):
                logger.info('Next maintenance block number found: %s' % block)
                maintenance_block = block
                start_time = get_time_from_line(line)
                logger.info('Start maintenance time: %s' % start_time)
                break
    for line in file_lines:
        if 'Finished in block=#%s' % maintenance_block in line:
            finish_time = get_time_from_line(line)
            logger.info('Finish maintenance time: %s' % finish_time)
            break

    time_in_ms = calculate_maintenance_time(start_time, finish_time)
    return time_in_ms


def write_to_result_file(file_path, value):
    with open(file_path, 'w') as f:
        f.write('Original BitShare,Stock Asset Worker\n')
        f.write(value)


def append_comma_separated_value_to_file(file_path, value):
    with open(file_path, 'a') as f:
        value_with_comma = ',%s' % value
        f.write(value_with_comma)


def write_result_to_csv(file_path, value):
    str_value = str(value)
    if os.path.exists(file_path):
        append_comma_separated_value_to_file(file_path, str_value)
    else:
        write_to_result_file(file_path, str_value)


def calculate_account_reward_amount(asset, asset_amount, asset_percent,
                                    reward_percent, account_percent):

    asset_reward_amount = calculate_full_reward_amount(asset, asset_amount,
                                                       asset_percent,
                                                       reward_percent)
    logger.info('Calculate account asset reward amounts')
    account_asset_reward_amount = calculate_percent(
        asset_reward_amount, account_percent, bitshares_value=False)
    return account_asset_reward_amount


def calculate_full_fee(asset, asset_amount, asset_percent):
    precision_value = 10 ** asset.precision
    logger.info('Get assets full fees')
    asset_full_fee = calculate_percent(
        asset_amount * precision_value, asset_percent)
    logger.info('"%s" asset full fee: %s' % (asset.name, asset_full_fee))
    return asset_full_fee


def calculate_full_reward_amount(asset, asset_amount, asset_percent,
                                 reward_percent):
    asset_full_fee = calculate_full_fee(asset, asset_amount, asset_percent)
    logger.info('Calculate assets reward amounts')
    asset_reward_amount = calculate_percent(asset_full_fee, reward_percent)
    return asset_reward_amount


def prepare_dmf_asset_options(extensions, flags_int=DMF_ASSET_FLAG,
                              permissions_int=DMF_ASSET_FLAG,
                              max_market_fee=100000):
    options = {"max_supply": 1000000000,
               "market_fee_percent": 0,
               "max_market_fee": max_market_fee,
               "issuer_permissions": permissions_int,
               "flags": flags_int,
               "extensions": extensions,
               "core_exchange_rate": {
                   "base": {
                       "amount": 10,
                       "asset_id": "1.3.0"},
                   "quote": {
                       "amount": 10,
                       "asset_id": "1.3.1"}},
               "whitelist_authorities": [],
               "blacklist_authorities": [],
               "whitelist_markets": [],
               "blacklist_markets": [],
               "description": "DMF test asset description"
               }
    return options


def check_irreversible_block_is_updated():
    count_of_witnesses = len(CLI_WALLET.get_active_witnesses())
    irreversible_block_before = CLI_WALLET.get_last_irreversible_block_num()
    logger.info('Irreversible block before: %s' % irreversible_block_before)
    for _ in xrange(count_of_witnesses):
        wait_blocks(1)
        irreversible_block = CLI_WALLET.get_last_irreversible_block_num()
        logger.info('Current irreversible block: %s' % irreversible_block)
        if irreversible_block > irreversible_block_before:
            logger.info('Consensus is achieved')
            break
    else:
        raise AssertionError('Consensus is not achieved')


def create_account_update_operation_auth(account_id, owner_weight_threshold=1,
                                         owner_account_auths=list(),
                                         active_weight_threshold=1,
                                         active_account_auths=list()):
    account_update_operation = {
        "account": account_id,
        "owner": {
            "weight_threshold": owner_weight_threshold,
            "account_auths": owner_account_auths,
            "key_auths": [],
            "address_auths": []
        },
        "active": {
            "weight_threshold": active_weight_threshold,
            "account_auths": active_account_auths,
            "key_auths": [],
            "address_auths": []
        },
        "extensions": {}
    }
    return account_update_operation
