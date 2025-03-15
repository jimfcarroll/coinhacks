import json
from dataclasses import dataclass

from xrpl import CryptoAlgorithm
from xrpl.clients import JsonRpcClient
from xrpl.core.keypairs import (derive_classic_address, derive_keypair,
                                is_valid_message, sign)


@dataclass
class Config:
    public_key: str
    private_key: str
    xrp_address: str
    client_url: str = "https://xrplcluster.com" # Alternative: "https://s1.ripple.com:51234"

    _client: JsonRpcClient = None

    def client(self) -> JsonRpcClient :
        if not self._client:
            self._client = JsonRpcClient(self.client_url)
        return self._client

def validate(config : Config | dict) -> Config:
    if config is None:
        raise ValueError("Invalid Config: None")
    
    if isinstance(config, dict):
        config = Config(**config)
    if not config.private_key:
        raise ValueError("Invalid Config: missing private_key")
    if not config.public_key:
        raise ValueError("Invalid Config: missing public_key")
    if not config.xrp_address:
        raise ValueError("Invalid Config: missing account")
    
    # Validate the public_key is the public_key for the given private key
    # Message to sign
    message = "test message".encode("utf-8")
    # Sign the message using the private key
    signature = sign(message, config.private_key)
    if not is_valid_message(message=message, signature=bytes.fromhex(signature), public_key=config.public_key):
        raise ValueError(f"Invalid Config: The public key {config.public_key} doesn't seem to be paired with the private key.")

    # Validate the address is in sync with the public_key
    classic_address = derive_classic_address(config.public_key)
    if classic_address != config.xrp_address:
        raise ValueError(f"Invalid Config: Address given was {config.xrp_address} however, the address generated from the public key was {classic_address}")
    return config

def calculate_config(seed: str) -> Config:
    public_key, private_key = derive_keypair(seed, algorithm=CryptoAlgorithm.SECP256K1)
    classic_address = derive_classic_address(public_key)
    config = Config(public_key=public_key, private_key=private_key, xrp_address=classic_address)
    return config

def load_config(file_path: str) -> Config:
    return validate(_load_config(file_path))

def _load_config(file_path : str) -> dict:
    """Load a JSON config file into a Python dictionary."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
    

