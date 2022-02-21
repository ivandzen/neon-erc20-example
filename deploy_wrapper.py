from erc20_wrapper import ERC20Wrapper
from common import *

wrapper = ERC20Wrapper.deploy(
    'TestToken2', 
    'TTOK2', 
    solana_client,
    neon_client,
    TEST_TOKEN_MINT,
    neon_account)

print(f'ERC20 wrapper {wrapper.eth_contract_address} created for SPL token {TEST_TOKEN_MINT}')