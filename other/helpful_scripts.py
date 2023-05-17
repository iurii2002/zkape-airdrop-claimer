import json

from eth_typing import HexStr
from typing import List
from loguru import logger
from pathlib import Path
from web3 import Account, Web3
from web3.exceptions import BadFunctionCallOutput
from zksync2.core.types import EthBlockParams
from eth_account.signers.local import LocalAccount
from eth_account.account import ChecksumAddress
from zksync2.core.types import ZkBlockParams
from zksync2.transaction.transaction_builders import TxFunctionCall
from zksync2.transaction.transaction712 import Transaction712
from zksync2.signer.eth_signer import PrivateKeyEthSigner
from zksync2.module.module_builder import ZkSyncBuilder
from other.providers import get_provider


abi_files = {
    'erc20': 'files/abis/erc20.json',
}


def _create_transaction_params(
        account: LocalAccount, zk_w3: Web3, call_data: HexStr, to: HexStr, value: int = 0) \
        -> Transaction712:

    func_call = TxFunctionCall(chain_id=zk_w3.zksync.chain_id,
                               nonce=zk_w3.zksync.get_transaction_count(account.address, ZkBlockParams.COMMITTED.value),
                               from_=account.address,
                               to=to,
                               data=call_data,
                               gas_limit=0,
                               gas_price=zk_w3.zksync.gas_price,
                               value=value,
                               max_priority_fee_per_gas=100000000)

    estimate_gas = zk_w3.zksync.eth_estimate_gas(func_call.tx)
    tx_712 = func_call.tx712(estimated_gas=estimate_gas)
    return tx_712


def send_eip712_transaction(zk_w3: Web3, account: LocalAccount, data: HexStr, to: HexStr, value: int = 0):
    signer = PrivateKeyEthSigner(account, zk_w3.zksync.chain_id)
    tx = _create_transaction_params(account=account, zk_w3=zk_w3, call_data=data, value=value, to=to)
    singed_message = signer.sign_typed_data(tx.to_eip712_struct())
    msg = tx.encode(singed_message)
    tx_hash = zk_w3.zksync.send_raw_transaction(msg)
    tx_receipt = zk_w3.zksync.wait_for_transaction_receipt(tx_hash, timeout=240, poll_latency=0.5)
    logger.info(f"Tx status: {tx_receipt['status']}")
    logger.info(f"Tx hash: {tx_receipt['transactionHash'].hex()}")


def load_accounts_from_keys(path: str) -> List[LocalAccount]:
    file = Path(path).open()
    return [Account.from_key(line.replace("\n", "")) for line in file.readlines()]


def get_balance(wallet: ChecksumAddress, symbol: str, zk_w3: Web3, token_address: ChecksumAddress = None) -> int:
    if symbol != 'eth':
        if token_address is None:
            logger.error("wrong input")
            raise ValueError

        erc20_contract = zk_w3.zksync.contract(token_address, abi=json.load(Path(abi_files['erc20']).open()))
        try:
            balance = erc20_contract.functions.balanceOf(wallet).call()
        except BadFunctionCallOutput:
            balance = "n/a"
        return balance

    else:
        balance = zk_w3.zksync.get_balance(wallet, EthBlockParams.LATEST.value)
    return balance


def get_eth_balance(wallet: ChecksumAddress, zk_w3: Web3) -> int:
    return get_balance(wallet, 'eth', zk_w3)


def get_zksync_w3(network: str):
    if network == 'testnet':
        return ZkSyncBuilder.build(get_provider('Zksync_era_testnet'))
    elif network == 'mainnet':
        return ZkSyncBuilder.build(get_provider('Zksync_era'))
