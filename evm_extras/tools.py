import os
import json
from web3 import AsyncWeb3, Web3
from typing import Optional
from typing import Literal, get_args
from python_extras import in_literal, snake_case
from evm_extras.exceptions import InvalidToken
from evm_extras.exceptions import ContractNotFound
from functools import wraps, lru_cache
from evm_wallet.types import Network
from evm_extras.types import ContractMap


@lru_cache()
def load_contracts(
        provider: AsyncWeb3 | Web3,
        defi: str,
        network: Network | str,
        contracts_path: str,
        version: Optional[int] = None
) -> ContractMap:
    """
    Load contract data from JSON and ABI files.

    Function requires, that snake-cased defi name match with corresponding folder containing data of contracts.

    Folder structure:
    contracts/
    │
    ├── defi1/
    │   ├── contracts.json
    │   ├── contract1.abi
    │   └── contract2.abi
    │
    └── defi2/
        ├── contracts.json
        ├── contract1.abi
        └── contract2.abi

    If you want to support multiple versions of DeFi protocol, you must have the following folder structure. Sub-folder
    of DeFi folder must have the format "v<VERSION_NUMBER>"
    contracts/
    │
    └── defi/
        ├── v1/
        │   ├── contracts.json
        │   ├── contract1.abi
        │   └── contract2.abi
        │
        └── v2/
            ├── contracts.json
            └── contract1.abi


    Structure of contracts.json:
    {
      "contract1": {
        "abi": "contract1.abi",
        "address": {
          "Arbitrum": "0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f",
          "Optimism": "0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f"
        }
      },
      "contract2": {
        "abi": "contract2.abi",
        "address": {
          "Arbitrum": "0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f",
          "Optimism": "0x2B4069517957735bE00ceE0fadAE88a26365528f",
        }
      }
    }

    :param provider: An instance of AsyncWeb3 or Web3.
    :param defi: The name of the DeFi.
    :param network: The network name.
    :param contracts_path: The path to the directory containing folders with contracts.json and ABI files.
    :param version: Optional version number of the DeFi protocol. Specify when DeFi folder contains multiple sub-folders
                    for specific versions of DeFi protocol.
    :return: A dictionary mapping contract names to their corresponding contracts or ABI names to their corresponding ABIs.
    """
    folder_name = snake_case(defi)
    path = os.path.join(contracts_path, folder_name)

    if version:
        path = os.path.join(contracts_path, f'v{version}')

    contract_data = {}
    with open(f"{path}/contracts.json") as file:
        content = json.load(file)
        contract_names = content.keys()

        for name in contract_names:
            contract_content = content[name]
            if 'address' in contract_content:
                addresses = contract_content['address']
                if network not in addresses:
                    raise ContractNotFound(defi, network, addresses.keys())

                contract_data[name] = {'address': addresses[network], 'abi_path': contract_content['abi']}
            else:
                contract_data[name] = {'abi_path': contract_content['abi']}

    for name in contract_names:
        with open(os.path.join(path, contract_data[name]['abi_path'])) as file:
            abi = json.load(file)
            if name in contract_data:
                contract_data[name]['abi'] = abi
            else:
                contract_data[f"{name}_abi"] = {'abi': abi}

    contracts = {}
    for key, value in contract_data.items():
        abi = value['abi']

        address = value.get('address')
        contracts[key] = provider.eth.contract(address=address, abi=abi) if address else abi

    return contracts


def validate_network(func):
    """Decorator to reload contracts of DeFi before executing method if wallet instance changed the network."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        network = self.network
        wallet = self.wallet

        if network != wallet.network:
            defi = self._defi_name or self.__class__.__name__

            try:
                version = self.version
            except AttributeError:
                version = None

            contracts = load_contracts(wallet.provider, defi, wallet.network['network'], version)

            for key, value in contracts.items():
                setattr(self, f'_{key}', value)

            self._network = wallet.network
            self._provider = wallet.provider

        return func(self, *args, **kwargs)

    return wrapper


def validate_token(
        token: str,
        token_literal: Literal,
        network: str,
        defi: str
) -> None:
    """
    Validate if the given token is in the specified Literal type.

    :param token: The token to be validated.
    :param token_literal: The Literal type representing valid tokens.
    :param network: The network identifier or name.
    :param defi: The name of the DeFi protocol.
    :raises InvalidToken: If the token is not in the specified Literal type.
    """
    if not in_literal(token, token_literal):
        raise InvalidToken(token, network, defi, get_args(token_literal))
