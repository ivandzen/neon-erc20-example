# Example of wrapping SPL token by ERC2-20 interface in Neon

## Requirements

[Install solana CLI to your computer](https://docs.solana.com/ru/cli/install-solana-cli-tools)
[Install SPL Token program](https://spl.solana.com/token)

## Steps

1. Find your solana wallet address by typing in command line:

  > solana address
  
2. Airdrop some SOLs to your wallet address from [here](http://solfaucet.com) *NOTE* Make sure you airdropping to devnet

3. Check that balance is non-zero (1 SOL will be enough):
  
  > solana --url devnet balance
  
4. Connect your metamask wallet to Neon Devnet using this settings:
    - New RPC URL: https://proxy.devnet.neonlabs.org/solana
    - Chain ID: 245022926
    - Currency Symbol (optional): NEON
    
5. Airdrop some NEONs to your wallet by [this](https://neonswap.live/#/get-tokens) link - will drop maximum 10 tokens at a time.
    
6. cd to this file's parent directory in command line

8. Generate keypair for new SPL token:

  > solana-keygen new -o test-token-mint.json --force
  
  You will be asked for passphrase (can skip this step by pressing Enter)
    
7. Create new SPL token by running command:
   
  > spl-token --url devnet create-token -- test-token-mint.json
  
  Copy Base59 encoded string returned by this command in line like:
  
  > Creating token 3CZZw1DhdzhmWkCBddvDFcPHJsRzG4SktcYg6MtNKY5Z

8. Convert this Base58 address representation into HEX using [this service](https://appdevtools.com/base58-encoder-decoder) and copy resulting value

9. Replace 3rd argument of NeonERC20Wrapper (line 58) by value got on previous step *NOTE* Add 0x prefix to it
  
10. Load ERC20Example.sol file into [Remix](https://remix.ethereum.org) then compile and deploy it using Injected Web3 Environment on page "Deploy & run transactions" *NOTE* you should be connected to the same Metamask account that was supplied with airdrop on step 5 and to the same network that was setup on step 4.

11. Call getWrappedAddress function and copy resulting ERC20 wrapper contract address

12. Import newly created token into Metamask. Balance should be 0

12. Run mint_erc20_wrapped_token.py script with 2 arguments:
  - first - contract address got on the step 11
  - second - your Metamask wallet address
  
  For example:
  
    > python3 mint_erc20_wrapped_token.py 0xb19665132A95e06887e085564e43635eCC24e139 0xf71c4DACa893E5333982e2956C5ED9B648818376
    
  After successfull execution balance should change to 1000
