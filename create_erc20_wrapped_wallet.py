#!/bin/python3

from os.path import expanduser, join
from solana.rpc.api import Client
from solana.account import Account
from solana.publickey import PublicKey
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.system_program import SYS_PROGRAM_ID
from solana.sysvar import SYSVAR_RENT_PUBKEY
from solana.rpc.types import TxOpts
import json
import sys


with open("test-token-mint.json") as f:
    d = json.load(f)
token_mint = Account(d[0:32])   

if len(sys.argv) != 3:
    print("Usage: create_erc20_wrapped_wallet.py <wrapper_address> <neon_wallet_address>")
    exit(1)

# Eth-compatible address of ERC20 wrapper contract
# Substitute right value after deploying ERC20 wrapper contract
ERC20_CONTRACT_ADDRESS=sys.argv[1]

# Eth-compatible address of Neon account
# This should be your Metamask account address
NEON_WALLET_ADDRESS=sys.argv[2]

# DO NOT CHANGE!
EVM_LOADER_ID=PublicKey('eeLSJgWzzxrqKv1UxtRVVH8FX3qCQWUs9QuAjJpETGU')  

# Loading payer account data
# All transactions will be signed by this account
# NOTE: Make sure you have non-zero balance by running in command line: 
#    solana --url devnet balance
# You can airdrop some SOLs here: http://solfaucet.com
home = expanduser("~")
with open(join(home, ".config/solana/id.json")) as f:
    d = json.load(f)
payer = Account(d[0:32])


# Prepare Eth addresses for seeds
erc20_wrapper_address_bytes = bytes.fromhex(ERC20_CONTRACT_ADDRESS[2:])
neon_wallet_address_bytes = bytes.fromhex(NEON_WALLET_ADDRESS[2:])

# Calculate address of destination erc20 token account to mint SPL token to it
seeds = [b"\1", 
         b"ERC20Balance",
         bytes(token_mint.public_key()),
         erc20_wrapper_address_bytes,
         neon_wallet_address_bytes]
         
sol_erc20_token_account_address: PublicKey = PublicKey.find_program_address(seeds, EVM_LOADER_ID)[0]

# Calculate address of NEON account which erc20 token account is linked to
seeds = [b"\1", neon_wallet_address_bytes]
sol_neon_token_account_address: PublicKey = PublicKey.find_program_address(seeds, EVM_LOADER_ID)[0]

# Calculate Solana address of erc20 wrapper contract
seeds = [b"\1", erc20_wrapper_address_bytes]
sol_erc20_contract_address: PublicKey = PublicKey.find_program_address(seeds, EVM_LOADER_ID)[0]

# Creating destination ERC20 token account
trx = Transaction()
trx.add(
    TransactionInstruction(
        program_id=EVM_LOADER_ID,
        data=bytes.fromhex('0F'),
        keys=[
            AccountMeta(pubkey=payer.public_key(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=sol_erc20_token_account_address, is_signer=False, is_writable=True),
            AccountMeta(pubkey=sol_neon_token_account_address, is_signer=False, is_writable=True),
            AccountMeta(pubkey=sol_erc20_contract_address, is_signer=False, is_writable=True),
            AccountMeta(pubkey=token_mint.public_key(), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ]
    )
)

# Establishing solana connection and creating token management interface
client = Client('https://api.devnet.solana.com')

signers=[payer]
client.send_transaction(trx, *signers, opts=TxOpts(skip_confirmation=False, skip_preflight=False))

print(sol_erc20_token_account_address)