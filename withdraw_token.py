from erc20_wrapper import ERC20Wrapper
from solana.rpc.api import Client as SolanaClient
from solana.account import Account as SolanaAccount
from eth_keys.datatypes import PrivateKey as NeonPrivateKey
from solana.publickey import PublicKey
from web3 import Web3
from os.path import expanduser, join
import json
import sys

TOKEN_MINT = PublicKey(sys.argv[1])
ERC20_CONTRACT_ADDRESS = sys.argv[2]
AMOUNT = 100

# Creating connectors
solana_client = SolanaClient('https://api.devnet.solana.com')
neon_client = Web3(Web3.HTTPProvider('https://proxy.devnet.neonlabs.org/solana'))

interface_abi = None
with open('./erc20_iface.json', 'r') as f:
    interface_abi = json.load(f)

# Creating accounts
home = expanduser("~")
with open(join(home, ".config/solana/id3.json")) as f:
    d = json.load(f)
solana_acc = SolanaAccount(d[0:32])
neon_account = neon_client.eth.account.from_key(NeonPrivateKey(bytes.fromhex('f5cc5e36108264bc26e33616287a34eeaab06bffc6890e7db40d53e7821b382a')))  

wrapper = ERC20Wrapper(
    solana_client,
    neon_client,
    TOKEN_MINT,
    ERC20_CONTRACT_ADDRESS,
    interface_abi)

wrapper.withdraw(neon_account, solana_acc.public_key(), AMOUNT, solana_acc)