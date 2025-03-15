import sys

from btccli.btc_keys import make_bitcoin_keyset
from btccli.electrum import load_electrum_export

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} path/to/electrum/export.json")
    sys.exit(1)

electrum_export_path = sys.argv[1]

# Electrum export load
electrum_keys = load_electrum_export(electrum_export_path)

for btc_addr, electrum_wif_key in electrum_keys.items():
    bck = make_bitcoin_keyset(electrum_wif_key, known_electrum_addr=btc_addr)
    print(bck)
    assert btc_addr == bck.addr_segwit

