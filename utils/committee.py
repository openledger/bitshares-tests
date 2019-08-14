from utils.testutil import (get_expiration_time, get_last_operation,
                            wait_for_maintenance_after, wait_blocks)
import dateutil.parser as dt
from cli_wallet import CLI_WALLET
from utils.py_logger import logger


class Committee(object):
    def increaseBalance(self, fromAccount, amount):
        CLI_WALLET.transfer(fromAccount, "committee-account", amount)

    def addMember(self, account, member):
        CLI_WALLET.try_send_request("vote_for_committee_member",
                                    [account, member, False, True])
        CLI_WALLET.send_request("vote_for_committee_member",
                                [account, member, True, True])

    def deleteMember(self, account, member):
        CLI_WALLET.send_request("vote_for_committee_member",
                                [account, member, False, True])

    def members(self):
        obj = CLI_WALLET.get_object("1.2.0")
        return obj[0]["active"]["account_auths"]

    def update_global_property(self, member1, member2, field_name, value):
        logger.info('Updating %s to "%s"...' % (field_name, value))
        expiration = get_expiration_time(7 * CLI_WALLET.get_block_interval())

        CLI_WALLET.propose_parameter_change(
            [member1, expiration, {field_name: value}, True])

        wait_blocks(1)

        operation = get_last_operation(member1)

        proposal_id = operation["result"][1]

        CLI_WALLET.approve_proposal(member1, proposal_id)
        CLI_WALLET.approve_proposal(member2, proposal_id)

        wait_for_maintenance_after(dt.parse(expiration))
