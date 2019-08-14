from testutil import generate_random_string
from cli_wallet import CLI_WALLET
from py_logger import logger


class Asset(object):
    def __init__(self, registrar, precision=1, name=None):
        self.registrar = registrar
        self.precision = precision
        self.name = generate_random_string(7).upper() if name is None else name
        self._id = None

    @property
    def id(self):
        if self._id is None:
            self._id = CLI_WALLET.get_asset_id_by_symbol(self.name)
        return self._id

    def issue_asset(self, start_balance):
        response = CLI_WALLET.send_request(
            "issue_asset", [self.registrar, start_balance, self.name, "",
                            True])
        return response

    def get_options(self):
        response = CLI_WALLET.send_request("get_asset", [self.name])
        return response["result"]["options"]

    def update_options(self, new_options):
        response = CLI_WALLET.update_asset(self.name, None, new_options)
        return response

    def try_update_options(self, new_options):
        logger.info(
            'Trying to update "%s" asset with following options: %s' % (
                self.name, new_options))
        response = CLI_WALLET.try_send_request(
            "update_asset", [self.name, None, new_options, True])
        return response

    def transfer_to(self, user_name, amount):
        CLI_WALLET.transfer(
            self.registrar, user_name, amount, asset=self.name)

    def get_accumulated_fees(self):
        accumulated_fees = CLI_WALLET.get_accumulated_fees(self.id)
        return accumulated_fees
