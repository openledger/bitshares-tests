from utils.py_logger import log_step, logger
from utils.account import create_account_with_balance
from utils.b3_exceptions import BitshareStatusCodeError


def test_try_to_create_self_locked_account():
    log_step('Create account')
    account = create_account_with_balance()

    log_step('Try to create selflocked account')
    try:
        account.update_authorities(1, [[account.id, 1]], 1, [[account.id, 1]])
        raise AssertionError('Account %s is locked' % account.name)
    except BitshareStatusCodeError as e:
        error_message = 'Missing Authority %s' % account.id
        assert error_message in e.message['error']['message']
        logger.info('Error message is got')


def test_try_to_link_account_to_account_with_empty_authority():
    log_step('Create account')
    account = create_account_with_balance()

    log_step('Try to link account to account with empty authorities')
    try:
        account.update_authorities(1, [['1.2.3', 1]], 1, [['1.2.3', 1]])
        raise AssertionError('Account %s is locked' % account.name)
    except BitshareStatusCodeError as e:
        error_message = 'Missing Authority %s' % account.id
        assert error_message in e.message['error']['message']
        logger.info('Error message is got')


def test_try_to_lock_account_via_cycle():
    log_step('Create 3 accounts')
    account_1 = create_account_with_balance()
    account_2 = create_account_with_balance()
    account_3 = create_account_with_balance()

    log_step('Set account_2 to account_1 authorities')
    account_1.update_authorities(
        1, [[account_2.id, 1]], 1, [[account_2.id, 1]])

    log_step('Set account_3 to account_2 authorities')
    account_2.update_authorities(
        1, [[account_3.id, 1]], 1, [[account_3.id, 1]])

    log_step('Try to set account_1 to account_3 authorities')
    try:
        account_3.update_authorities(
            1, [[account_1.id, 1]], 1, [[account_1.id, 1]])
        raise AssertionError('Account %s is locked' % account_3.name)
    except BitshareStatusCodeError as e:
        error_message = 'Missing Authority %s' % account_3.id
        assert error_message in e.message['error']['message']
        logger.info('Error message is got')


def test_create_locked_in_depth_account():
    log_step('Create 4 accounts')

    account_1 = create_account_with_balance()
    account_2 = create_account_with_balance()
    account_3 = create_account_with_balance()
    account_4 = create_account_with_balance()

    log_step('Link account_1 authorities to account_2')
    account_1.update_authorities(
        1, [[account_2.id, 1]], 1, [[account_2.id, 1]])

    log_step('Link account_2 authorities to account_3')
    account_2.update_authorities(
        1, [[account_3.id, 1]], 1, [[account_3.id, 1]])

    log_step('Try to link account_3 authorities to account_4')
    account_3.update_authorities(
            1, [[account_4.id, 1]], 1, [[account_4.id, 1]])

    log_step('Try to do transfer by locked account_1 and check error message')
    try:
        account_1.transfer('init0', 10)
        raise AssertionError('Account %s is not locked' % account_1.name)
    except BitshareStatusCodeError as e:
        error_message = 'Missing Active Authority %s' % account_1.id
        assert error_message in e.message['error']['message']
        logger.info('Error message is got')


def test_create_locked_in_depth_account_reverse_order():
    log_step('Create 4 accounts')

    account_1 = create_account_with_balance()
    account_2 = create_account_with_balance()
    account_3 = create_account_with_balance()
    account_4 = create_account_with_balance()

    log_step('Link account_3 authorities to account_4')
    account_3.update_authorities(
        1, [[account_4.id, 1]], 1, [[account_4.id, 1]])

    log_step('Link account_2 authorities to account_3')
    account_2.update_authorities(
        1, [[account_3.id, 1]], 1, [[account_3.id, 1]])

    log_step('Try to link account_1 authorities to account_2')
    try:
        account_1.update_authorities(
            1, [[account_2.id, 1]], 1, [[account_2.id, 1]])
        raise AssertionError('Account %s is locked' % account_1.name)
    except BitshareStatusCodeError as e:
        error_message = 'Missing Authority %s' % account_1.id
        assert error_message in e.message['error']['message']
        logger.info('Error message is got')
