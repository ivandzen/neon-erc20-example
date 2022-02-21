from solana.rpc.api import Client as SolanaClient
from web3 import Web3
from eth_keys.datatypes import PrivateKey as NeonPrivateKey
from os.path import expanduser, join
from solana.account import Account as SolanaAccount
from solana.publickey import PublicKey
import json

# Connectors
solana_client = SolanaClient('https://api.devnet.solana.com')
neon_client = Web3(Web3.HTTPProvider('https://proxy.devnet.neonlabs.org/solana'))

# Accounts

neon_account = neon_client.eth.account.from_key(NeonPrivateKey(bytes.fromhex('f5cc5e36108264bc26e33616287a34eeaab06bffc6890e7db40d53e7821b382a')))

home = expanduser("~")
with open(join(home, ".config/solana/id.json")) as f:
    d = json.load(f)
solana_account = SolanaAccount(d[0:32])     

TEST_TOKEN_MINT = PublicKey('B5yv59YHm2caQd4BCB97Ws36Qo9dxokou3T3Dw2zjM9h')