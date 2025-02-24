import yfinance as yf
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import Fee
from xrpcli.config import Config

def _get_xrp_usd_price() -> float:
    """Fetches the current XRP/USD price from Yahoo Finance."""
    try:
        # Fetch the XRP-USD ticker data
        ticker = yf.Ticker("XRP-USD")
        # Get the latest market price
        xrp_price = ticker.history(period="1d")['Close'].iloc[-1]
        return xrp_price
    except Exception as e:
        print(f"❌ Failed to fetch XRP price: {e}")
        return None

def get_xrp_fees(config: Config):
    """Fetches the current transaction fees on the XRP Ledger."""

    client : JsonRpcClient = config.client()

    fee_request = Fee()
    response = client.request(fee_request)

    if response.is_successful():
        fees = response.result["drops"]
        base_fee_xrp = int(fees["base_fee"]) / 1_000_000
        min_fee_xrp = int(fees["minimum_fee"]) / 1_000_000
        median_fee_xrp = int(fees["median_fee"]) / 1_000_000
        open_ledger_fee_xrp = int(fees["open_ledger_fee"]) / 1_000_000
        
        print("📊 Current XRP Transaction Fees:")
        print(f"🔹 Base Fee (Per Fee Unit): {base_fee_xrp:.6f} XRP")
        print(f"🔹 Minimum Fee: {min_fee_xrp:.6f} XRP")
        print(f"🔹 Median Network Fee: {median_fee_xrp:.6f} XRP")
        print(f"🔹 Open Ledger Fee (Real-Time): {open_ledger_fee_xrp:.6f} XRP")
        return {
            "base_fee": base_fee_xrp,
            "minimum_fee": min_fee_xrp,
            "median_fee": median_fee_xrp,
            "open_ledger_fee": open_ledger_fee_xrp
        }
    else:
        print(f"❌ Error fetching fees: {response.result.get('error_message', 'Unknown error')}")
        return None

# Example usage
_xrp_price = None

def get_xrp_usd_price() -> float:
    global _xrp_price
    if _xrp_price is None:
        _xrp_price = _get_xrp_usd_price()

    return _xrp_price