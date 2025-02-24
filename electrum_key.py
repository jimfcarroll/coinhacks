from btccli.btc_keys import make_bitcoin_keyset
from btccli.electrum import load_electrum_export

# Electrum export load
electrum_keys = load_electrum_export('/home/jim/src/wallets/electrum-private-keys-default_wallet.json')

for btc_addr, electrum_wif_key in electrum_keys.items():
    bck = make_bitcoin_keyset(electrum_wif_key, known_electrum_addr=btc_addr)
    print(bck)
    assert btc_addr == bck.addr_segwit

