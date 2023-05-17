from loguru import logger

providers = {
    'zksync_era_testnet': 'https://testnet.era.zksync.dev',
    'zksync_era': 'https://mainnet.era.zksync.io',
}


def get_provider(chain):
    chain = chain.lower().capitalize()
    provider = ''
    if chain == 'Zksync_era':
        provider = providers['zksync_era']
    elif chain == 'Zksync_era_testnet':
        provider = providers['zksync_era_testnet']
    else:
        logger.error(f'{chain} not found')
    return provider
