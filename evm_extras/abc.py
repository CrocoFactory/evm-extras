from abc import ABC
from typing import Optional
from web3 import AsyncWeb3
from evm_wallet import AsyncWallet, NetworkInfo, Wallet


class Defi(ABC):
    """Abstract base class for interacting with decentralized finance (DeFi) protocols."""

    def __init__(
            self,
            wallet: AsyncWallet | Wallet,
            defi_name: str,
            version: Optional[int] = None
    ):
        """
        :param wallet: An instance of AsyncWallet or Wallet.
        :param defi_name: Name of the specific DeFi.
        :param version: Optional version number of the DeFi protocol.
        """
        self.__wallet = wallet
        self._network = wallet.network
        self._provider = wallet.provider
        self._defi_name = defi_name
        self._version = version

    @property
    def wallet(self) -> AsyncWallet | Wallet:
        """
        Get the wallet instance associated with this DeFi instance.

        :return: An instance of AsyncWallet or Wallet.
        """
        return self.__wallet

    @property
    def network(self) -> NetworkInfo:
        """
        Get information about the network associated with the wallet instance.

        :return: Dictionary containing information about the network.
        :rtype: NetworkInfo
        """
        return self._network

    @property
    def provider(self) -> AsyncWeb3:
        """
        Get the AsyncWeb3 provider associated with the wallet instance.

        :return: An instance of AsyncWeb3.
        """
        return self.provider

    @property
    def version(self) -> int | None:
        """
        Get the version number of the DeFi protocol.

        :return: Version number if available, otherwise None.
        """
        return self._version
