// SPDX-License-Identifier: MIT

pragma solidity >=0.5.12;

// ERC20 contract interface definition 
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

// Default implementation of NEON's ERC20 wrapper contract
contract NeonERC20Wrapper {
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

// Testing
contract ERC20WrapperTest {
    NeonERC20Wrapper private wrapper;

    constructor() {
        wrapper = new NeonERC20Wrapper("TestToken", "TTOK", 0x98403300ac23caa27ffa585216f39dcc2ab26b26792506ff4e931e56fc9c31a9);
    }

    function getWrapperAddress() external view returns (address) {
        return address(wrapper);
    }

    function TestTransfer(uint256 amount) external {
        address from = msg.sender;
        address to = 0x563d1fbB37385434C85B6564B9A85714C421f0c4;
        IERC20 erc20wrapped = IERC20(address(wrapper));

        uint256 beginBalance = erc20wrapped.balanceOf(to);
        require(erc20wrapped.transferFrom(from, to, amount));
        uint256 endBalance = erc20wrapped.balanceOf(to);
        require(endBalance - beginBalance == amount);
    }
}


