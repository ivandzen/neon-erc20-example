require("@nomiclabs/hardhat-waffle");
const Web3 = require('web3');
const axios = require('axios');

// This is a sample Hardhat task. To learn how to create your own go to
// https://hardhat.org/guides/create-task.html
task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(account.address);
  }
});

const proxy_url = 'https://proxy.devnet.neonlabs.org/solana';
const faucet_url = 'https://neonswap.live/request_eth_token';
const network_id = 245022926;

const web3 = new Web3(
  new Web3.providers.HttpProvider(proxy_url, 3000000)
);

const requestFaucet = async (wallet, amount) => {
  console.log('Requesting faucet...');
  const data = { amount: amount, wallet: wallet };
  console.log(`URL: ${faucet_url}`);
  console.log(`Wallet = ${data.wallet}, amount = ${data.amount}`);
  try {
    const result = await axios.post(faucet_url, data);
    console.log(result);
  } catch (err) {
    console.log(`Failed to send request to faucet: ${err}`);
  }
};

const getBalance = async (address) => await web3.eth.getBalance(address);

const requestFaucetAndGetBalance = async (address, amount) => {
  await requestFaucet(address, amount);
  await getBalance(address);
};

const acc = web3.eth.accounts.create();
(async (address, amount) => requestFaucetAndGetBalance(address, amount))(
  acc.address,
  10
);


/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: "0.8.4",
  defaultNetwork: 'neonlabs',
  networks: {
    neonlabs: {
      url: proxy_url,
      accounts: [acc.privateKey],
      network_id: network_id,
      chainId: network_id,
      gas: 3000000,
      gasPrice: 1000000000,
      blockGasLimit: 10000000,
      allowUnlimitedContractSize: false,
      timeout: 1000000,
      isFork: true
    }
  }
};
