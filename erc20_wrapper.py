from solcx import install_solc
from web3 import Web3
from solana.publickey import PublicKey
from solana.account import Account as SolanaAccount
from solana.rpc.api import Client as SolanaClient
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solana.rpc.commitment import Commitment
from construct import Bytes, Int8ul
from construct import Struct
from solana.system_program import SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.sysvar import SYSVAR_RENT_PUBKEY
from solana.rpc.types import TxOpts
from eth_account.signers.local import LocalAccount as NeonAccount
import struct
install_solc(version='0.7.6')
from solcx import compile_source

Confirmed = Commitment("confirmed")

EVM_LOADER_ID = PublicKey('eeLSJgWzzxrqKv1UxtRVVH8FX3qCQWUs9QuAjJpETGU')

CREATE_ACCOUNT_LAYOUT = Struct(
    "ether" / Bytes(20),
    "nonce" / Int8ul
)

def create_account_layout(ether, nonce):
    return bytes.fromhex("18")+CREATE_ACCOUNT_LAYOUT.build(dict(
        ether=ether,
        nonce=nonce
    ))

# Standard interface of ERC20 contract to generate ABI for wrapper
ERC20_INTERFACE_SOURCE = '''
pragma solidity >=0.7.0;

interface IERC20 {
    function decimals() external view returns (uint8);
    function totalSupply() external view returns (uint256);
    function balanceOf(address who) external view returns (uint256);
    function allowance(address owner, address spender) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function approve(address spender, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);


    function approveSolana(bytes32 spender, uint64 value) external returns (bool);
    event ApprovalSolana(address indexed owner, bytes32 indexed spender, uint64 value);
}
'''


# Copy of contract: https://github.com/neonlabsorg/neon-evm/blob/develop/evm_loader/SPL_ERC20_Wrapper.sol
ERC20_CONTRACT_SOURCE = '''
// SPDX-License-Identifier: MIT

pragma solidity >=0.5.12;

/*abstract*/ contract NeonERC20Wrapper /*is IERC20*/ {
    address constant NeonERC20 = 0xff00000000000000000000000000000000000001;

    string public name;
    string public symbol;
    bytes32 public tokenMint;

    constructor(
        string memory _name,
        string memory _symbol,
        bytes32 _tokenMint
    ) {
        name = _name;
        symbol = _symbol;
        tokenMint = _tokenMint;
    }

    fallback() external {
        bytes memory call_data = abi.encodePacked(tokenMint, msg.data);
        (bool success, bytes memory result) = NeonERC20.delegatecall(call_data);

        require(success, string(result));

        assembly {
            return(add(result, 0x20), mload(result))
        }
    }
}
'''


class ERC20Wrapper:
    def __init__(self,
                 solana_client: SolanaClient,
                 neon_client: Web3,
                 token_mint: PublicKey,
                 eth_contract_address: str,
                 interface,
                 wrapper):
        self.solana_client = solana_client
        self.neon_client = neon_client
        self.token_mint = token_mint
        self.eth_contract_address = eth_contract_address
        self.solana_contract_address = self.eth_to_solana_address(self.eth_contract_address)
        self.interface = interface
        self.wrapper = wrapper

    @staticmethod
    def deploy(name: str,
               symbol: str,
               solana_client: SolanaClient,
               neon_client: Web3,
               token_mint: PublicKey,
               payer: NeonAccount):
        compiled_interface = compile_source(ERC20_INTERFACE_SOURCE)
        _, interface = compiled_interface.popitem()

        compiled_wrapper = compile_source(ERC20_CONTRACT_SOURCE)
        _, wrapper = compiled_wrapper.popitem()

        erc20 = neon_client.eth.contract(abi=wrapper['abi'], bytecode=wrapper['bin'])
        nonce = neon_client.eth.get_transaction_count(payer.address)
        tx = {'nonce': nonce}
        tx_constructor = erc20.constructor(name, symbol, bytes(token_mint)).buildTransaction(tx)
        tx_deploy = neon_client.eth.account.sign_transaction(tx_constructor, payer.key)
        tx_deploy_hash = neon_client.eth.send_raw_transaction(tx_deploy.rawTransaction)
        tx_deploy_receipt = neon_client.eth.wait_for_transaction_receipt(tx_deploy_hash)
        eth_contract_address = tx_deploy_receipt.contractAddress
        return ERC20Wrapper(
            solana_client,
            neon_client,
            token_mint,
            eth_contract_address,
            interface,
            wrapper)
        

    def eth_to_solana_address(self, eth_account_address: str) -> PublicKey:
        eth_account_addressbytes = bytes.fromhex(eth_account_address[2:])
        return PublicKey.find_program_address([b"\1", eth_account_addressbytes], EVM_LOADER_ID)

    def get_wrapped_token_account_address(self, eth_account_address: str) -> PublicKey:
        eth_contract_address_bytes = bytes.fromhex(self.eth_contract_address[2:])
        eth_account_address_bytes = bytes.fromhex(eth_account_address[2:])
        seeds = [b"\1", b"ERC20Balance",
                 bytes(self.token_mint),
                 eth_contract_address_bytes,
                 eth_account_address_bytes]
        return PublicKey.find_program_address(seeds, EVM_LOADER_ID)[0]

    def is_account_exist(self, acc: PublicKey):
        acc_info_resp = self.solana_client.get_account_info(acc, Confirmed)
        if acc_info_resp.get('result', None) is None:
            raise RuntimeError(f'Failed to retrieve account {acc}')

        return not acc_info_resp['result'].get('value', None) is None

    def deposit(self, 
                source_sol: SolanaAccount, 
                dest_neon: str, 
                amount: int,
                payer: SolanaAccount = None):
        """
        Transfer tokens from token wallet associated with source Solana account 
        to destination Neon account  
        """
        source_token_acc = get_associated_token_address(source_sol.public_key(), self.token_mint)
        if not self.is_account_exist(source_token_acc):
            raise RuntimeError(f'Source associated token account {source_token_acc} does not exist')

        if payer is None:
            payer = source_sol

        trx = Transaction()
        root_acc, nonce = self.eth_to_solana_address(dest_neon)
        if not self.is_account_exist(root_acc):
            data = create_account_layout(bytes(dest_neon[2:]), nonce)
            trx.add(TransactionInstruction(
                program_id=EVM_LOADER_ID,
                data=data,
                keys=[
                    AccountMeta(pubkey=payer.public_key(), is_signer=True, is_writable=True),
                    AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=PublicKey(root_acc), is_signer=False, is_writable=True),
                ]))

        dest_token_account = self.get_wrapped_token_account_address(dest_neon)
        if not self.is_account_exist(dest_token_account):
            trx.add(TransactionInstruction(
                program_id=EVM_LOADER_ID,
                data=bytes.fromhex('0F'),
                keys=[
                    AccountMeta(pubkey=payer.public_key(), is_signer=True, is_writable=True),
                    AccountMeta(pubkey=dest_token_account, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=root_acc, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=self.solana_contract_address, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=self.token_mint, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
                ]
            ))

        trx.add(TransactionInstruction(
            program_id=TOKEN_PROGRAM_ID,
            data=b'\3' + struct.pack('<Q', amount),
            keys=[
                AccountMeta(pubkey=source_token_acc, is_signer=False, is_writable=True),
                AccountMeta(pubkey=dest_token_account, is_signer=False, is_writable=True),
                AccountMeta(pubkey=payer.public_key(), is_signer=True, is_writable=False)
            ]
        ))

        opts = TxOpts(skip_preflight=True, skip_confirmation=False)
        return self.solana_client.send_transaction(trx, payer, opts=opts)

    def withdraw(self,
                 source_neon: NeonAccount,
                 dest_sol: SolanaAccount,
                 amount: int):
        source_token_account = self.get_wrapped_token_account_address(source_neon)
        if not self.is_account_exist(source_token_account):
            raise RuntimeError(f'Source token account {source_token_account} not exist')
        
        dest_token_account = get_associated_token_address(dest_sol.public_key(), self.token_mint)
        if not self.is_account_exist(dest_token_account):
            trx = Transaction()
            trx.add(
                create_associated_token_account(
                    dest_sol.public_key(), 
                    dest_sol.public_key, 
                    self.token_mint
                )
            )

            opts = TxOpts(skip_preflight=True, skip_confirmation=False)
            print(self.solana_client.send_transaction(trx, dest_sol, opts))







from eth_keys.datatypes import PrivateKey as NeonPrivateKey

neon_client = Web3('https://proxy.devnet.neonlabs.org/solana')
eth_account = neon_client.eth.account.from_key(NeonPrivateKey(bytes.fromhex('f5cc5e36108264bc26e33616287a34eeaab06bffc6890e7db40d53e7821b382a')))        

wrapper = ERC20Wrapper.deploy(
    'TestToken2', 
    'TTOK2', 
    SolanaClient('https://api.devnet.solana.com'),
    Web3('https://proxy.devnet.neonlabs.org/solana'),
    PublicKey('B5yv59YHm2caQd4BCB97Ws36Qo9dxokou3T3Dw2zjM9h'),
    eth_account)
