from erc20_wrapper import ERC20Wrapper
from solana.publickey import PublicKey
from solana.account import Account as SolanaAccount
from solana.rpc.api import Client as SolanaClient
from web3 import Web3
from os.path import expanduser, join
import json
import sys

TOKEN_MINT = PublicKey(sys.argv[1])
ERC20_CONTRACT_ADDRESS = sys.argv[2]
DEST_NEON = sys.argv[3]
AMOUNT = int(sys.argv[4])

print(f'Deposit {AMOUNT} tokens {TOKEN_MINT} wrapped with {ERC20_CONTRACT_ADDRESS} to {DEST_NEON}')

solana_client = SolanaClient('https://api.devnet.solana.com')
neon_client = Web3(Web3.HTTPProvider('https://proxy.devnet.neonlabs.org/solana'))

wrapper = ERC20Wrapper(
    solana_client,
    neon_client,
    TOKEN_MINT,
    ERC20_CONTRACT_ADDRESS,
    None) #interface not used

home = expanduser("~")
with open(join(home, ".config/solana/id.json")) as f:
    d = json.load(f)
solana_acc = SolanaAccount(d[0:32])

wrapper.deposit(solana_acc, DEST_NEON, AMOUNT)