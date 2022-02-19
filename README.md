# Example of wrapping SPL token by ERC-20 interface in Neon

## Requirements

  - [Install solana CLI to your computer](https://docs.solana.com/ru/cli/install-solana-cli-tools)
  - [Install SPL Token program](https://spl.solana.com/token)
  - python3 and pip3 installed
  - install python requirements:
    
    > pip3 install -r requirements.txt

## Steps

1. Make sure you are on devnet solana:
  > solana config get
  
  RPC URL should be https://api.devnet.solana.com
  
  Evaluate command if not:
  > solana config set --url devnet 

2. Find your solana wallet address by typing in command line:

  > solana address
  
3. Airdrop some SOLs to your wallet address from [here](http://solfaucet.com) *NOTE* Make sure you airdropping to devnet

4. Check that balance is non-zero (1 SOL will be enough):
  
  > solana balance

### Prepare Solana side

5. cd to this file's parent directory in command line

6. Generate keypair for new SPL token:
  > solana-keygen new -o test-token-mint.json --force
  
  You will be asked for passphrase (may skip this step by pressing Enter)
  test-token-mint.json file now contains private key of your SPL token. Now we will extract it's public key to environment variable using solana tool:
  > AWESOME_TOKEN_ADDRESS=$(solana address -k test-token-mint.json)
    
7. Create new SPL token by running command:
  > spl-token create-token -- test-token-mint.json

8. Create associated token account using token mint address got on previous step:
  > spl-token create-account $AWESOME_TOKEN_ADDRESS

  After succesfull execution of this command you will get address of your new token account and signature of the transaction

9. Mint some tokens to just created wallet:
  > spl-token mint $AWESOME_TOKEN_ADDRESS 1000

10. Check balance
  > spl-token balance $AWESOME_TOKEN_ADDRESS


### Prepare Neon side

10. First of all, let's decode base58 encoded token address to HEX representation and copy resulting output:
  > printf ${AWESOME_TOKEN_ADDRESS} | base58 -d | xxd -p

  Sometimes there will be two or more strings in the output, something like this:
  > 761784519394f3fb582a88072a13dc0bd71ffb7e09253fe0b20e6b8faf66
  >
  > b20a

  Don't worry, this is because of the way this piping works, just copy all the lines and then remove newline characters:
  > 761784519394f3fb582a88072a13dc0bd71ffb7e09253fe0b20e6b8faf66b20a

11. Replace tokenMint value in file ERC20Example.sol (line 16) by value got on previous step *NOTE* Add 0x prefix to it

12. Connect your metamask wallet to Neon Devnet using this settings:
    - New RPC URL: https://proxy.devnet.neonlabs.org/solana
    - Chain ID: 245022926
    - Currency Symbol (optional): NEON
    
13. Airdrop some NEONs to your wallet by [this](https://neonswap.live/#/get-tokens) link - will drop maximum 10 tokens at a time.
  
14. Load ERC20Example.sol file into [Remix](https://remix.ethereum.org) then compile and deploy it using Injected Web3 Environment on page "Deploy & run transactions".

15. Copy ERC20 contract address

16. Import newly created token into Metamask. Balance should be 0

### Transfer from Solana to Neon

17. Run create_erc20_wrapped_wallet.py script with 2 arguments:
  - first - contract address got on the step 11
  - second - your Metamask wallet address
  
  For example:
  
    > python3 mint_erc20_wrapped_token.py 0x4ced59EF4b7bEdaA1f5DB17D9F71E7B1bd7C5bea 0xf71c4DACa893E5333982e2956C5ED9B648818376
    

