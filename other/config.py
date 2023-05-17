from web3 import Web3

addresses = {
    'usdc': Web3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),
    'zat': Web3.to_checksum_address('0x47EF4A5641992A72CFd57b9406c9D9cefEE8e0C4'),
    'eth': Web3.to_checksum_address('0x000000000000000000000000000000000000800a'),
    'weth': Web3.to_checksum_address('0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'),
}

sleeping_time_min = 10
sleeping_time_max = 15
