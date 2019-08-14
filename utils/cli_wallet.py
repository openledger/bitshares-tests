from connection import JsonRpc
from constants import DEFAULT_CORE_ASSET
import dateutil.parser as dt
from utils.py_logger import logger
from b3_exceptions import BitshareConditionError
from vesting_balances import VestingBalance
from decimal import Decimal


class CliWallet(object):
    def __init__(self, uri):
        self.rpc = JsonRpc(uri)

    def send_request(self, method, *arguments, **kwargs):
        # args_param = arguments[0] if arguments else []
        # cmd = 'curl --data \'{"jsonrpc": "2.0", "method": "%s", ' \
        #       '"params": %s, "id": 1}\' %s' % \
        #       (method, args_param, self.rpc.uri)
        # logger.debug('Execute: %s' % cmd)
        response = self.rpc.send_request(method, *arguments, **kwargs)
        # logger.debug('%s\n' % response)
        return response

    def try_send_request(self, method, *arguments, **kwargs):
        kwargs.update(expected_code=None)
        logger.debug('Try send "%s" request...' % method)
        result = self.send_request(method, *arguments, **kwargs)
        return result

    def transfer(self, from_account, to_account, amount,
                 asset=DEFAULT_CORE_ASSET):
        logger.info(
            'Transferring %s %s from "%s" to "%s"' % (
                amount, asset, from_account, to_account))
        response = self.send_request(
            "transfer", [from_account, to_account, amount, asset, "", True])
        return response

    def get_account_balance(self, account):
        response = self.send_request("list_account_balances",
                                     [account])
        return response["result"]

    def get_dict_account_balance(self, account):
        logger.info('Get %s account balance and combine it to dict' % account)
        response = self.send_request("list_account_balances",
                                     [account])
        balances_list = response["result"]
        balances_dict = combine_balances(balances_list)
        logger.info('%s balance: %s' % (account, balances_dict))
        return balances_dict

    def get_asset_account_balance(self, account,
                                  asset_name=DEFAULT_CORE_ASSET):
        result = self.get_account_balance(account)

        if 0 < len(result):
            for asset_balance in result:
                asset_symbol = self.get_asset_symbol_by_id(
                    asset_balance["asset_id"])
                if asset_symbol == asset_name:
                    return int(asset_balance["amount"])
        return 0

    def get_core_account_balance(self, account):
        return self.get_asset_account_balance(account, DEFAULT_CORE_ASSET)

    def register_account(
            self, name, pub_key_owner, pub_key_active, registrar_account,
            referrer_account, referrer_percent="0", broadcast=True):
        logger.info(
            'Registering new account. Name: "{0}". Registrar: "{1}".'
            ' Referrer: "{2}". Referrer percent: {3}'.format(
                name, registrar_account, referrer_account, referrer_percent))
        result = self.send_request(
            "register_account", [name, pub_key_owner, pub_key_active,
                                 registrar_account, referrer_account,
                                 referrer_percent, broadcast])
        return result

    def get_current_supply(self, asset_id='1.3.0'):
        asset_data = self.get_object(asset_id)
        dynamic_asset_data_id = asset_data[0]['dynamic_asset_data_id']
        dynamic_asset_data = self.get_object(dynamic_asset_data_id)
        current_supply = dynamic_asset_data[0]['current_supply']
        return current_supply

    def get_object(self, obj):
        return self.send_request("get_object", [obj])["result"]

    def get_account(self, account):
        return self.send_request("get_account", [account])["result"]

    def get_asset(self, symbol_or_id):
        return self.send_request("get_asset", [symbol_or_id])["result"]

    def get_asset_symbol_by_id(self, asset_id):
        response = self.send_request("get_asset", [asset_id])
        return response["result"]["symbol"]

    def get_asset_id_by_symbol(self, asset_symbol):
        response = self.send_request("get_asset", [asset_symbol])
        return response["result"]["id"]

    def sell_asset(self, seller, amount_to_sell, symbol_to_sell,
                   minimum_to_receive, symbol_to_receive, timeout):
        logger.info(
            'Selling %s "%s" asset by "%s". %s "%s" to receive. Timeout: %s.'
            % (amount_to_sell, symbol_to_sell, seller, minimum_to_receive,
               symbol_to_receive, timeout))
        response = self.send_request(
            "sell_asset", [seller, amount_to_sell, symbol_to_sell,
                           minimum_to_receive, symbol_to_receive, timeout,
                           False, True])
        return response["result"]

    def get_dynamic_global_properties(self):
        response = self.send_request("get_dynamic_global_properties")
        return response["result"]

    def get_head_block_number(self):
        return self.get_dynamic_global_properties()["head_block_number"]

    def get_current_witness(self):
        return self.get_dynamic_global_properties()["current_witness"]

    def get_global_properties(self):
        response = self.send_request("get_global_properties")
        return response["result"]

    def get_global_parameters(self):
        return self.get_global_properties()["parameters"]

    def get_block_interval(self):
        return self.get_global_parameters()["block_interval"]

    def get_gas_price(self):
        return self.get_global_parameters()["gas_price"]

    def get_gas_limit(self):
        return self.get_global_parameters()["gas_limit"]

    def get_maintenance_interval(self):
        return self.get_global_parameters()["maintenance_interval"]

    def get_next_maintenance_time(self):
        prop = self.get_dynamic_global_properties()
        return dt.parse(prop["next_maintenance_time"])

    def propose_parameter_change(self, *args):
        self.send_request("propose_parameter_change", *args)

    def approve_proposal(self, account, proposal):
        args = [account, proposal, {"active_approvals_to_add": [account]},
                True]
        self.send_request("approve_proposal", args)

    def create_account_with_private_key(self, key, name, registrar):
        response = self.send_request("create_account_with_private_key",
                                     [key, name, registrar, True])
        return response

    def get_list_committee_members(self, lowerbound='', limit=1000):
        response = self.send_request('list_committee_members',
                                     [lowerbound, limit])
        return response['result']

    def get_id_of_committee_member(self, account_name):
        id = self.get_list_committee_members(lowerbound=account_name, limit=1)
        return id[0][1]

    def vote_for_committee_member(self, voting_account, account, approve,
                                  broadcast=True):
        response = self.send_request(
            "vote_for_committee_member", [voting_account, account, approve,
                                          broadcast])
        return response

    def try_vote_for_witness(self, voting_account, witness):
        self.try_send_request(
            "vote_for_witness", [voting_account, witness, True, True])

    def get_witness(self, witness):
        return self.send_request("get_witness", [witness])["result"]

    def list_witnesses(self):
        return self.send_request("list_witnesses", ["", 1000])["result"]

    def create_asset(self, account_name, asset_name, precision, options,
                     bitasset_opts):
        # if bitasset_opts is None - asset type will be "user asset"
        # if bitasset_opts is {} - asset type will be "market asset"
        logger.info(
            'Creating "%s" asset by %s' % (asset_name, account_name))
        response = self.send_request(
            "create_asset",
            [account_name, asset_name, precision, options, bitasset_opts,
             True])
        return response['result']

    def issue_asset(self, account, amount, asset_name, memo=''):
        logger.info(
            'Issuing %s "%s" asset by %s' % (amount, asset_name, account))
        response = CLI_WALLET.send_request(
            "issue_asset", [account, amount, asset_name, memo, True])
        return response['result']

    def get_block(self, number):
        response = self.send_request("get_block", [number])
        return response["result"]

    def publish_asset_feed(self, account_name, asset_name, price_feed):
        logger.info(
            'Publishing "%s" asset with %s price feed by %s' % (
                asset_name, price_feed, account_name))
        response = self.send_request(
            "publish_asset_feed",
            [account_name, asset_name, price_feed, True])
        return response["result"]

    def borrow_asset(self, seller_name, amount_to_borrow, asset_name,
                     amount_of_collateral):
        logger.info(
            'Borrowing "%s" asset to %s amount by %s with %s' % (
                asset_name, amount_to_borrow, seller_name,
                amount_of_collateral))
        response = self.send_request(
            "borrow_asset", [seller_name, amount_to_borrow, asset_name,
                             amount_of_collateral, True])
        return response['result']

    def upgrade_account(self, account_to_upgrade):
        logger.info(
            'Upgrading "%s" account to lifetime...' % account_to_upgrade)
        response = self.send_request(
            "upgrade_account", [account_to_upgrade, True])
        return response['result']

    def get_accumulated_fees(self, asset_id):
        logger.info('Getting accumulated fee for %s asset' % asset_id)
        asset_data = self.get_object(asset_id)
        dynamic_asset_data_id = asset_data[0]['dynamic_asset_data_id']
        dynamic_asset_data = self.get_object(dynamic_asset_data_id)
        accumulated_fees = dynamic_asset_data[0]['accumulated_fees']
        logger.info(
            'Accumulated fee for %s: %s' % (asset_id, accumulated_fees))
        return accumulated_fees

    def withdraw_vesting(self, vesting_balance_id, asset, amount):
        prepared_amount = prepare_amount_to_claim(amount, asset.precision)
        logger.info(
            'Withdraw vesting %s "%s" asset reward for %s' % (
                prepared_amount, asset.name, vesting_balance_id))
        response = self.send_request(
            "withdraw_vesting", [vesting_balance_id, prepared_amount,
                                 asset.name, True])
        return response['result']

    def get_mfs_vesting_balance(self, account_name, asset_id):
        logger.info(
            'Getting %s asset reward for %s' % (asset_id, account_name))
        mfs_vesting_balances_list = self.get_mfs_vesting_balances_list(
            account_name)
        for mfs_vb_object in mfs_vesting_balances_list:
            if mfs_vb_object.asset_id == asset_id:
                break
        else:
            raise BitshareConditionError(
                '"%s" is not in asset rewards list:\n%s' % (
                    asset_id, mfs_vesting_balances_list))
        logger.info(
            '%s asset reward for %s account is got: %s. ID: %s' % (
                mfs_vb_object.asset_id, account_name,
                mfs_vb_object.asset_amount, mfs_vb_object.id))
        return mfs_vb_object

    def get_mfs_vesting_balances_list(self, account_name):
        """Returns list of MfsVestingBalance objects"""
        logger.info(
            'Getting vesting balances for %s' % account_name)
        response = self.send_request(
            "get_vesting_balances", [account_name])
        vb_list = response['result']
        mfs_vb_objects_list = list()
        for vb_json in vb_list:
            if vb_json['balance_type'] == 'market_fee_sharing':
                mfs_vb_objects_list.append(VestingBalance(vb_json))
                logger.info(
                    'MFS vesting balances for %s account is got:\n%s' % (
                        account_name, vb_json))
        return mfs_vb_objects_list

    def get_limit_orders(self, asset_id_1, asset_id_2, limit=10):
        logger.info(
            'Getting limit orders. Asset_id_1: "%s". Asset_id_2: "%s".'
            ' Limit: %s' % (asset_id_1, asset_id_2, limit))
        response = self.send_request(
            "get_limit_orders", [asset_id_1, asset_id_2, limit])
        result = response['result']
        logger.info('Limit orders are got: %s' % result)
        return result

    def update_asset(self, symbol, new_issuer, new_options):
        logger.info(
            'Updating "%s" asset. New issuer: "%s". New options: %s' % (
                symbol, new_issuer, new_options))
        response = self.send_request(
            "update_asset", [symbol, new_issuer, new_options, True])
        result = response['result']
        logger.info('%s asset updated: %s' % (symbol, result))
        return result

    def whitelist_account(self, authorizing_account, account_to_list,
                          new_listing_status):
        logger.info(
            '"%s" account is "%s" by "%s"' % (
                account_to_list, new_listing_status, authorizing_account))
        response = self.send_request(
            "whitelist_account",
            [authorizing_account, account_to_list, new_listing_status, True])
        result = response['result']
        logger.info('%s is %s\n%s' % (
            account_to_list, new_listing_status, result))
        return result

    def get_trade_statistics_object(self, account_id, asset_id):
        logger.info(
            'Getting trade statistics for %s. Asset id: %s' % (account_id,
                                                               asset_id))
        response = self.send_request("get_trade_statistics", [account_id,
                                                              asset_id])
        return response['result']

    def get_trade_statistics(self, account_id, asset_id):
        trade_statistics_object = self.get_trade_statistics_object(account_id,
                                                                   asset_id)
        amount = trade_statistics_object['total_volume']['amount']
        logger.info('Trade statistics amount: %s' % amount)
        return amount

    def get_last_irreversible_block_num(self):
        dynamic_global_properties = self.get_dynamic_global_properties()
        return dynamic_global_properties["last_irreversible_block_num"]

    def get_active_witnesses(self):
        global_properties = self.get_global_properties()
        return global_properties["active_witnesses"]

    def add_operation_to_builder_transaction(self, transaction_handle,
                                             account_update_operation):
        self.send_request(
            'add_operation_to_builder_transaction',
            [transaction_handle, [6, account_update_operation]])

    def get_transaction_handle(self):
        result = self.send_request('begin_builder_transaction')['result']
        logger.info('Transaction handle is got: %s' % result)
        return result

    def set_fees_on_builder_transaction(self, transaction_handle):
        result = self.send_request(
            'set_fees_on_builder_transaction',
            [transaction_handle, DEFAULT_CORE_ASSET])['result']
        logger.info('Fees for transaction: %s' % result)
        return result

    def sign_builder_transaction(self, transaction_handle):
        result = self.send_request(
            'sign_builder_transaction', [transaction_handle, True])['result']
        logger.info('Transaction: %s' % result)
        return result


def combine_balances(balances_list):
    result_dict = dict()
    for balance in balances_list:
        result_dict[balance['asset_id']] = balance['amount']
    return result_dict


def prepare_amount_to_claim(amount, precision):
    precision_value = 10 ** precision
    result = Decimal(amount) / Decimal(precision_value)
    return str(result)


# default cli wallet uri
uri = 'http://%s:%s' % ('localhost', 7092)
CLI_WALLET = CliWallet(uri)
