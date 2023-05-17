import datetime
import random
import time

from loguru import logger
from sys import stderr

from modules.zkape import claim
from other.helpful_scripts import load_accounts_from_keys, get_eth_balance, get_zksync_w3
from other.config import sleeping_time_min, sleeping_time_max


# FILE SETTINGS
file_keys = 'files/keys'
file_log = 'logs/mainnet_log'


def load_logger():
    # LOGGING SETTING
    logger.remove()
    logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - "
                              "<white>{message}</white>")
    logger.add(file_log + f"{datetime.datetime.now().strftime('%Y%m%d')}.log",
               format="<white>{time:HH:mm:ss}</white> | "
                      "<level>{level: <8}</level> | "
                      "<cyan>{line}</cyan> - <white>{"
                      "message}</white>")


def main_script():
    accounts = load_accounts_from_keys(file_keys)
    zksync_web3 = get_zksync_w3('mainnet')

    random.shuffle(accounts)

    for account in accounts:
        load_logger()
        logger.info(f'Started for wallet {account.address}')
        try:
            if get_eth_balance(wallet=account.address, zk_w3=zksync_web3):
                claim(zk_w3=zksync_web3, account=account)
            else:
                logger.info(f"Do not have balance on account {account.address}")
        except Exception as err:
            logger.error(f'Something went wrong with account {account.address} : {err}')

        random_sleep = random.randint(sleeping_time_min, sleeping_time_max)
        logger.info(f"Sleeping for {random_sleep} seconds")
        time.sleep(random_sleep)


if __name__ == '__main__':
    main_script()
