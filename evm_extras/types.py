from evm_wallet.types import ABI
from web3.contract import AsyncContract, Contract

ContractMap = dict[str, AsyncContract | ABI | Contract]
