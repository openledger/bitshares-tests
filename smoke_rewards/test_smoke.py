import pytest
from utils.cli_wallet import CLI_WALLET
from utils.witness_node import WITNESS_NODE
from utils.constants import DEFAULT_CORE_ASSET


def test_connect_to_witness_node(socket, witness_node):
    socket.connect(witness_node.host_port)
    assert socket


def test_connect_to_cli_wallet(socket, cli_wallet):
    socket.connect(cli_wallet.host_port)
    assert socket


def test_witness_node_request():
    response = WITNESS_NODE.send_request('get_chain_properties')
    assert response["result"]


@pytest.mark.parametrize('params', [[["1.2.0"]], [["1.2.1"]]])
@pytest.mark.parametrize('method_name', ['get_accounts'])
def test_witness_node_request_with_params(method_name, params):
    response = WITNESS_NODE.send_request(method_name, params)
    assert response["result"]


@pytest.mark.parametrize('params', ["init1", "init2", "init3"])
def test_cli_wallet_transfer(params):
    balance = CLI_WALLET.get_core_account_balance(params)

    amount_to_transfer = "1.234"
    CLI_WALLET.transfer('nathan', params, amount_to_transfer,
                        DEFAULT_CORE_ASSET)

    amount = CLI_WALLET.get_core_account_balance(params) - balance
    assert amount == int(float(amount_to_transfer) * 100000)
