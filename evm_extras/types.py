from web3.contract import AsyncContract, Contract
from web3.types import ABI

ContractMap = dict[str, AsyncContract | ABI | Contract]
