import os
import pytest
from web3.contract import AsyncContract

from evm_extras import load_contracts


@pytest.fixture()
def wallet(make_wallet):
    return make_wallet('Optimism')


@pytest.fixture
def contracts_path():
    package_path = os.path.dirname(os.path.abspath(__file__))
    contracts = os.path.join(package_path, 'contracts')
    return contracts


def test_load_contracts(wallet, contracts_path):
    contracts = load_contracts(wallet.provider, 'Circle', wallet.network['network'], contracts_path)

    assert isinstance(contracts['circle_relayer'], AsyncContract) and isinstance(contracts['token_messenger'], AsyncContract)
