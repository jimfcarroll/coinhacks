#import json
import sys
from dataclasses import asdict

from xrpl import CryptoAlgorithm
from xrpl.core.keypairs import derive_classic_address, derive_keypair
from xrpl.wallet import Wallet

from xrpcli.transactions import get_all_transactions,parse_xrp_transaction
from xrpcli.account import get_xrp_balance
from xrpcli.config import Config, calculate_config, validate
from xrpcli.utils import get_xrp_fees, get_xrp_usd_price

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} shfMySeed")
    sys.exit(1)

# Your XRP seed (starting with 'shf')
seed = sys.argv[1]

# Derive private and public keys
# public_key, private_key = derive_keypair(seed, algorithm=CryptoAlgorithm.SECP256K1)

# Derive the XRP address from the public key
# classic_address = derive_classic_address(public_key)

# print("Private Key:", private_key)
# print("Public Key:", public_key)
# print("XRP Address:", classic_address)

# wallet = Wallet.from_seed(seed, algorithm=CryptoAlgorithm.SECP256K1)

# print("XRP Address from Wallet:", wallet.address)

config = validate(calculate_config(seed))
#print("Config: ", json.dumps(asdict(config)))

# Print all of the transactions
for tx in get_all_transactions(config):
    parse_xrp_transaction(tx)

# get and print the current balance and value given the current price for XRP
balance = get_xrp_balance(config)
print(f"Current XRP Balance: {balance}")
dollars_per_xrp = get_xrp_usd_price()
print(f"Current Account Value: 💲{balance * dollars_per_xrp} at 💲{dollars_per_xrp} per XRP")

# print the current fees
print(get_xrp_fees(config))

