from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountTx
from xrpcli import config
from xrpcli.transactions import parse_xrp_transaction

config = config.load_config('config.json')

# Use a full-history XRPL node (try different nodes if needed)
client = JsonRpcClient("https://xrplcluster.com")  # Alternative: "https://s1.ripple.com:51234"

# Replace with your actual XRP Ledger address
account_address = config.xrp_address

# Pagination parameters
marker = None
all_transactions = []

while True:
    # Create an AccountTx request with pagination
    account_tx_request = AccountTx(
        account=account_address,
        ledger_index_min=0,  # Fetch from the earliest ledger
        ledger_index_max=-1, # Up to the latest ledger
        limit=10,            # Adjust limit per request
        marker=marker        # Continue from the last point if paginating
    )

    # Send the request
    response = client.request(account_tx_request)

    if response.is_successful():
        transactions = response.result.get("transactions", [])
        all_transactions.extend(transactions)

        # Check if there's more data to fetch
        marker = response.result.get("marker")
        if not marker:  # No more pages to fetch
            break
    else:
        print(f"Failed to retrieve transactions: {response.result.get('error_message', 'Unknown error')}")
        break

# Print all transactions
if all_transactions:
    for tx in all_transactions:
        parse_xrp_transaction(tx)
else:
    print("No transactions found in the specified ledger range.")

