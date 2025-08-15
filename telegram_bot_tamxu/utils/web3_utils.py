from web3 import Web3

ERC20_ABI = [{
    "constant": True,
    "inputs": [{"name": "_owner", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "balance", "type": "uint256"}],
    "type": "function"
}]

def get_token_balance(w3: Web3, token_address: str, user_address: str) -> float:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI
    )
    balance = contract.functions.balanceOf(Web3.to_checksum_address(user_address)).call()
    return balance / 10**18
