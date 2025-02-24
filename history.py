from typing import List

from xrpcli import config
from xrpcli.transactions import get_all_transactions, parse_xrp_transaction

config = config.load_config('config.json')

all_transactions: List[dict] = get_all_transactions(config)

# Print all transactions
if all_transactions:
    for tx in all_transactions:
        parse_xrp_transaction(tx)
else:
    print("No transactions found in the specified ledger range.")

