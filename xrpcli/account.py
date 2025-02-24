from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo
from xrpcli.config import Config

def get_xrp_balance(config: Config) -> float:
    """Fetches the XRP balance of an account."""
    client: JsonRpcClient = config.client()
    account_address: str = config.xrp_address
    account_info_request = AccountInfo(account=account_address, ledger_index="validated")
    response = client.request(account_info_request)

    if response.is_successful():
        balance_drops = response.result["account_data"]["Balance"]  # Balance in drops
        balance_xrp = int(balance_drops) / 1_000_000  # Convert drops to XRP
        return balance_xrp
    else:
        print("❌ Error fetching balance:", response.result.get("error_message", "Unknown error"))
        return None
