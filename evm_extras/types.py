from typing import Literal
from evm_wallet import ERC20Token
from web3.contract import AsyncContract, Contract
from web3.types import ABI

ContractMap = dict[str, AsyncContract | ABI | Contract]
NativeToken = Literal['AVAX', 'ETH', 'BNB', 'FTM', 'MATIC', '0x0000000000000000000000000000000000000000']
Token = ERC20Token | NativeToken