# Example of wrapping SPL token by ERC-20 interface in Neon

## Requirements

  - [Install solana CLI to your computer](https://docs.solana.com/ru/cli/install-solana-cli-tools)
  - [Install SPL Token program](https://spl.solana.com/token)
  - python3 and pip3 installed
  - install python requirements:
    
    > pip3 install -r requirements.txt

## Setup Solana account

1. Make sure you are on devnet solana:
  > solana config get
  
  RPC URL should be https://api.devnet.solana.com
  
  Evaluate command if not:
  > solana config set --url devnet 

2. Create new solana account. You will be asked for passphrase (may skip this step by pressing Enter)
  > solana-keygen new -o ~/.config/solana/id.json --force

3. Find your solana wallet address by typing in command line:
  > solana address
  
4. Airdrop some SOLs to your wallet address from [here](http://solfaucet.com) *NOTE* Make sure you airdropping to devnet

## Setup Neon account (using Metamask)

1. Create new account in Metamask

2. Copy new account's private key (Account Details >> Export Private Key)

3. Insert just copied private key into quotes in line 15 file common.py

4. Airdrop some NEONs to just created account [here](https://neonswap.live/#/get-tokens) 

## Create new token mint

1. cd to this file's parent directory in command line

2. Generate keypair for new SPL token:
  > solana-keygen new -o test-token-mint.json --force
  
  You will be asked for passphrase (may skip this step by pressing Enter)
  test-token-mint.json file now contains private key of your SPL token. Now we will extract it's public key to environment variable using solana tool:
  > AWESOME_TOKEN_ADDRESS=$(solana address -k test-token-mint.json)

3. Create new SPL token by running command:
  > spl-token -u devnet create-token -- test-token-mint.json

4. Copy value contained by AWESOME_TOKEN_ADDRESS
  > echo $AWESOME_TOKEN_ADDRESS

5. Insert this value into quotes in line 22 file common.py

## Creating ERC20 wrapper

1. > python3 deploy_wrapper.py

2. Save ERC20 wrapper address got in previous comand output.

3. Import just created token into Metamask.

## Minting tokens

1. Create associated token account using token mint address got on previous step:
  > spl-token -u devnet create-account $AWESOME_TOKEN_ADDRESS

  After succesfull execution of this command you will get address of your new token account and signature of the transaction

2. Mint some tokens to just created wallet:
  > spl-token -u devnet mint $AWESOME_TOKEN_ADDRESS 1000

3. Check balance
  > spl-token -u devnet balance $AWESOME_TOKEN_ADDRESS

## Depositing SPL tokens from Solana into Neon

1. Run deposit_token.py with two arguments:
  - address of ERC20 wrapper got on step 'Creating ERC20 wrapper'
  - amount
  > python3 deposit_token.py 0x5221D25fEDf90a01BE219be13C9D050C640Ea3A0 10000000000

## Withdrawing ERC20-wrapped SPL tokens from Neon to Solana

1. Run withdraw_token.py with two arguments:
  - address of ERC20 wrapper got on step 'Creating ERC20 wrapper'
  - amount
  > python3 withdraw_token.py 0x5221D25fEDf90a01BE219be13C9D050C640Ea3A0 1000000000
