class VestingBalance(object):

    def __init__(self, vesting_balance_receipt):
        receipt = vesting_balance_receipt

        self._id = receipt['id']
        self._balance = receipt['balance']
        self._allowed_withdraw = receipt['allowed_withdraw']
        self._owner = receipt['owner']
        self._balance_type = receipt['balance_type']

    @property
    def id(self):
        return self._id

    @property
    def balance(self):
        return self._balance

    @property
    def allowed_withdraw(self):
        return self._allowed_withdraw

    @property
    def owner(self):
        return self._owner

    @property
    def asset_id(self):
        return self._balance['asset_id']

    @property
    def asset_amount(self):
        return self._balance['amount']
