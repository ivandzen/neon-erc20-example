from solana.rpc.api import Client as SolanaClient
from web3 import Web3
from eth_keys.datatypes import PrivateKey as NeonPrivateKey
from os.path import expanduser, join
from solana.account import Account as SolanaAccount
from solana.publickey import PublicKey
import json
import os

# Connectors
solana_client = SolanaClient('https://api.devnet.solana.com')
neon_client = Web3(Web3.HTTPProvider('https://proxy.devnet.neonlabs.org/solana'))

# Accounts
neon_account = neon_client.eth.account.from_key(NeonPrivateKey(bytes.fromhex('a95f0b88ebb9abb2a5cc30960c31a66a5ed6293fb3d26eb825a26f36945ef55b')))

home = expanduser("~")
with open(join(home, ".config/solana/id.json")) as f:
    d = json.load(f)
solana_account = SolanaAccount(d[0:32])     

TEST_TOKEN_MINT = PublicKey(os.environ['AWESOME_TOKEN_ADDRESS'])