const hre = require("hardhat");

async function main() {
  const Wrapper = await hre.ethers.getContractFactory("NeonERC20Wrapper");
  const wrapper = await Wrapper.deploy();

  await wrapper.deployed();

  console.log("ERC20Wrapper deployed to:", wrapper.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
