from account import create_account_with_balance


def create_self_locked_account():
    account = create_account_with_balance()
    account.update_authorities(1, [[account.id, 1]], 1, [[account.id, 1]])
    return account


def create_linked_to_self_locked_account():
    self_locked_account = create_self_locked_account()
    linked_to_self_locked_account = create_account_with_balance()
    linked_to_self_locked_account.update_authorities(
        1, [[self_locked_account.id, 1]], 1, [[self_locked_account.id, 1]])
    return linked_to_self_locked_account


def create_cycled_accounts():
    account_1 = create_account_with_balance()
    account_2 = create_account_with_balance()
    account_3 = create_account_with_balance()

    account_1.update_authorities(
        1, [[account_2.id, 1]], 1, [[account_2.id, 1]])
    account_2.update_authorities(
        1, [[account_3.id, 1]], 1, [[account_3.id, 1]])
    account_3.update_authorities(
        1, [[account_1.id, 1]], 1, [[account_1.id, 1]])

    return account_1, account_2, account_3


def create_double_locked_accounts():
    account_1 = create_account_with_balance()
    account_2 = create_account_with_balance()
    account_3 = create_account_with_balance()

    account_1.update_authorities(
        1, [[account_2.id, 1]], 1, [[account_2.id, 1]])
    account_3.update_authorities(
        1, [[account_1.id, 1]], 1, [[account_1.id, 1]])

    account_1.update_authorities(
        1, [[account_3.id, 1]], 1, [[account_3.id, 1]])
    account_2.update_authorities(
        1, [[account_3.id, 1]], 1, [[account_3.id, 1]])

    return account_1, account_2, account_3
