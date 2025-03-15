from datetime import datetime
from xrpl.models.requests import AccountTx
from xrpcli.config import Config
from typing import List

# Lookup table for XRP Transaction Result Codes with correct explanations
XRPL_RESULT_CODES = {
    "tesSUCCESS": "✅ Success - Transaction applied to ledger",
    
    # Failures that still consume fees
    "tecUNFUNDED_PAYMENT": "❌ Failed - No XRP fee was provided when submitted",
    "tecPATH_DRY": "❌ Failed - Insufficient liquidity for payment",
    "tecNO_DST_INSUF_XRP": "❌ Failed - Destination requires XRP but has insufficient balance",
    "tecINSUFFICIENT_RESERVE": "❌ Failed - Account lacks required reserve",
    "tecINSUFFICIENT_PAYMENT": "❌ Failed - Payment amount too low",
    "tecNO_LINE": "❌ Failed - No trustline exists between sender and recipient",
    
    # Retryable errors (Transaction was not applied, but can be retried)
    "terRETRY": "🔄 Retry suggested - Transaction not applied yet",
    "terQUEUED": "🔄 Queued - Waiting for ledger processing",
    
    # Local errors (Rejected immediately, no fees charged)
    "telINSUF_FEE_P": "❌ Failed - Insufficient transaction fee",
    "telNO_DST": "❌ Failed - Destination account does not exist",
    
    # Hard failures (Rejected at server level)
    "tejMAX_LEDGER": "❌ Failed - Exceeded max ledger sequence",
    "tejINVALID": "❌ Failed - Invalid transaction format"
}

def get_all_transactions(config: Config) -> List[dict]:
    # Replace with your actual XRP Ledger address
    account_address = config.xrp_address

    # Pagination parameters
    marker = None
    all_transactions = []

    client = config.client()

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
    
    return all_transactions


def parse_xrp_transaction(tx):
    """Prints a human-readable summary of an XRP Ledger transaction."""

    tx_json = tx['tx_json']
    meta = tx['meta']
    
    # Convert XRP values from drops to XRP
    drops_to_xrp = lambda drops: f"{int(drops) / 1_000_000:.6f}" if drops else "Unknown"

    # Convert Ripple epoch time to local timezone
    def ripple_time_to_local(ripple_time):
        if ripple_time:
            unix_time = ripple_time + 946684800  # Ripple epoch starts at 2000-01-01
            local_time = datetime.fromtimestamp(unix_time).astimezone()  # Convert to local timezone
            return local_time.strftime("%Y-%m-%d %H:%M:%S %Z")  # Include timezone name
        return "Unknown"
    
    # Determine transaction status
    status = "Unknown"
    if meta:
        transaction_result = meta.get("TransactionResult", "Unknown")
        status = XRPL_RESULT_CODES.get(transaction_result, f"❌ Failed ({transaction_result})")

    # Extract transaction details
    account = tx_json.get("Account", "Unknown")
    destination = tx_json.get("Destination", "Unknown")
    amount = drops_to_xrp(tx_json.get("DeliverMax", tx_json.get("Amount", None)))  # Handle both fields
    fee = drops_to_xrp(tx_json.get("Fee", None))
    ledger_index = tx_json.get("ledger_index", "Unknown")
    transaction_type = tx_json.get("TransactionType", "Unknown")
    date = ripple_time_to_local(tx_json.get("date", None))
    sequence = tx_json.get("Sequence", "Unknown")
    last_ledger_sequence = tx_json.get("LastLedgerSequence", "Unknown")
    
    # Print transaction summary
    print("=" * 50)
    print(f"📜 XRP Transaction Summary")
    print("=" * 50)
    print(f"🔹 Transaction Type : {transaction_type}")
    print(f"🔹 Status           : {status}")
    print(f"🔹 Sender           : {account}")
    print(f"🔹 Recipient        : {destination}")
    print(f"🔹 Amount Sent      : {amount} XRP" if amount is not None else "🔹 Amount Sent      : Unknown")
    print(f"🔹 Transaction Fee  : {fee} XRP" if fee is not None else "🔹 Transaction Fee  : Unknown")
    print(f"🔹 Ledger Index     : {ledger_index}")
    print(f"🔹 Transaction Date : {date}")
    print(f"🔹 Sequence Number  : {sequence}")
    print(f"🔹 Last Ledger Seq  : {last_ledger_sequence}")
    print("=" * 50)

