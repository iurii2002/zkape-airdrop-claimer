import json
import requests
import random
import ua_generator

from loguru import logger
from web3 import Web3
from pathlib import Path
from eth_account.signers.local import LocalAccount

from other.helpful_scripts import send_eip712_transaction


abi_files = {
    'zat': 'files/abis/zat.json',
}


def get_headers() -> dict:
    referer = 'https://airdrop.zkape.io'
    browser = random.choice(('chrome', 'firefox', 'safari'))
    platform = random.choice(('android', 'ios'))
    ua = ua_generator.generate(device='mobile', platform=platform, browser=browser)
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': referer,
        'referer': f"{referer}/",
        'sec-ch-ua': f'"{ua.ch.brands[2:]}"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': f'"{ua.platform.title()}"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': ua.text,
    }
    return headers


def get_tx_parameters(wallet: str) -> tuple:
    url = 'https://zksync-ape-apis.zkape.io/airdrop/index/getcertificate'

    payload = {
        'address': wallet,
    }
    resp = requests.post(url=url, headers=get_headers(), json=payload)

    if resp.status_code == 200:
        try:
            data = resp.json()['Data']
            if int(data['value']) == 0:
                raise Exception("Nothing to claim")
            return (
                Web3.to_checksum_address(data['owner']),
                int(data['value']),
                int(data['nonce']),
                int(data['deadline']),
                int(data['v']),
                data['r'],
                data['s'],
            )
        except:
            print(f'{wallet} somthing went wrong')


def claim(zk_w3: Web3, account: LocalAccount):
    logger.info("Claiming ZAT")
    zat_claim_contract_address = Web3.to_checksum_address('0x9aA48260Dc222Ca19bdD1E964857f6a2015f4078')
    zat_claim_contract = zk_w3.zksync.contract(zat_claim_contract_address, abi=json.load(Path(abi_files['zat']).open()))
    tx_params = get_tx_parameters(account.address)
    call_data = zat_claim_contract.encodeABI('claim', tx_params)
    send_eip712_transaction(zk_w3=zk_w3, account=account, data=call_data, to=zat_claim_contract_address)
