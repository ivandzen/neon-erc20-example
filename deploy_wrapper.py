from solana.publickey import PublicKey
from solana.rpc.api import Client as SolanaClient
from web3 import Web3
from solana.account import Account as SolanaAccount
from erc20_wrapper import ERC20Wrapper
from eth_keys.datatypes import PrivateKey as NeonPrivateKey
from os.path import expanduser, join
import json

TEST_TOKEN_MINT = PublicKey('B5yv59YHm2caQd4BCB97Ws36Qo9dxokou3T3Dw2zjM9h')

# Creating connectors
solana_client = SolanaClient('https://api.devnet.solana.com')
neon_client = Web3(Web3.HTTPProvider('https://proxy.devnet.neonlabs.org/solana'))

# Creating accounts
home = expanduser("~")
with open(join(home, ".config/solana/id.json")) as f:
    d = json.load(f)
solana_acc = SolanaAccount(d[0:32])
neon_account = neon_client.eth.account.from_key(NeonPrivateKey(bytes.fromhex('f5cc5e36108264bc26e33616287a34eeaab06bffc6890e7db40d53e7821b382a')))        

wrapper = ERC20Wrapper.deploy(
    'TestToken2', 
    'TTOK2', 
    solana_client,
    neon_client,
    TEST_TOKEN_MINT,
    neon_account)

print(f'ERC20 wrapper {wrapper.eth_contract_address} created for SPL token {TEST_TOKEN_MINT}')