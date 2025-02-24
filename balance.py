from xrpcli.account import get_xrp_balance
from xrpcli.config import Config, load_config
from xrpcli.utils import get_xrp_usd_price, get_xrp_fees

config: Config = load_config('config.json')

balance = get_xrp_balance(config)

print(f"Current XRP Balance: {balance}")
dollars_per_xrp = get_xrp_usd_price()

print(f"Current Account Value: 💲{balance * dollars_per_xrp} at 💲{dollars_per_xrp} per XRP")

get_xrp_fees(config)