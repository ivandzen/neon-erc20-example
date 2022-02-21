# Example of wrapping SPL token by ERC-20 interface in Neon

## Requirements

  - [Install solana CLI to your computer](https://docs.solana.com/ru/cli/install-solana-cli-tools)
  - [Install SPL Token program](https://spl.solana.com/token)
  - python3 and pip3 installed
  - install python requirements:
    
    > pip3 install -r requirements.txt

## Setup Solana account

- Make sure you are on devnet solana:
  > solana config get
  
  RPC URL should be https://api.devnet.solana.com

  Evaluate command if not:
  > solana config set --url devnet 

- Create new solana account. You will be asked for passphrase (may skip this step by pressing Enter)
  > solana-keygen new -o ~/.config/solana/id.json --force

- Find your solana wallet address by typing in command line:
  > solana address

- Airdrop some SOLs to your wallet address from [here](http://solfaucet.com) *NOTE* Make sure you airdropping to devnet

## Setup Neon account (using Metamask)

- Create new account in Metamask
- Airdrop some NEONs to just created account [here](https://neonswap.live/#/get-tokens)
- Copy your Metamask account private key (Account Details >> Export Private Key)
- Insert just copied private key into quotes in line 15 in file **common.py**
- Insert just copied private key into quotes in line 5 in file **hardhat.config.py**

## Create new token mint

- cd to this file's parent directory in command line

- Generate keypair for new SPL token:
  > solana-keygen new -o test-token-mint.json --force
  
  You will be asked for passphrase (may skip this step by pressing Enter)
  test-token-mint.json file now contains private key of your SPL token. Now we will extract it's public key to environment variable using solana tool:
  > export AWESOME_TOKEN_ADDRESS=$(solana address -k test-token-mint.json)

- Create new SPL token by running command:
  > spl-token -u devnet create-token -- test-token-mint.json

## Creating ERC20 wrapper

### First way: Using python script

- Run deploy_wrapper.py script 
  > python3 deploy_wrapper.py
- Save ERC20 wrapper address got in previous comand output.
- Import just created token into Metamask.

### Second way: Using hardhat

- Install JS requirements:
  > npm i
- Compile contract
  > npx hardhat compile
- Deploy contract
  > npx hardhat run --network neonlabs scripts/deploy.js
- Import just created token into Metamask using it's address:
  > ERC20Wrapper deployed to: 0x5221D25fEDf90a01BE219be13C9D050C640Ea3A0

## Minting tokens

- Create associated token account using token mint address got on previous step:
  > spl-token -u devnet create-account $AWESOME_TOKEN_ADDRESS

  After succesfull execution of this command you will get address of your new token account and signature of the transaction

- Mint some tokens to just created wallet:
  > spl-token -u devnet mint $AWESOME_TOKEN_ADDRESS 1000

- Check balance
  > spl-token -u devnet balance $AWESOME_TOKEN_ADDRESS

## Depositing SPL tokens from Solana into Neon

- Run deposit_token.py with two arguments:
  - address of ERC20 wrapper got on step 'Creating ERC20 wrapper'
  - amount
  > python3 deposit_token.py 0x5221D25fEDf90a01BE219be13C9D050C640Ea3A0 10000000000

## Withdrawing ERC20-wrapped SPL tokens from Neon to Solana

- Run withdraw_token.py with two arguments:
  - address of ERC20 wrapper got on step 'Creating ERC20 wrapper'
  - amount
  > python3 withdraw_token.py 0x5221D25fEDf90a01BE219be13C9D050C640Ea3A0 1000000000
