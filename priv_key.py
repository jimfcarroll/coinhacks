from xrpcli import config
import sys

config = config.load_config('/home/jim/src/wallets/config.json')

print("Private Key:", config.private_key)
print("Public Key:", config.public_key)
print("XRP Address:", config.xrp_address)
