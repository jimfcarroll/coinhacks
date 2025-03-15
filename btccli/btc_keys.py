from dataclasses import dataclass

from btccli.keys import (comp_public_key_to_segwit_address,
                             comp_public_key_to_taproot_address,
                             comp_public_key_to_wrapped_segwit_address,
                             compressed_to_uncompressed_pubkey,
                             private_key_to_public_key, private_key_to_wif,
                             uncomp_public_key_to_legacy_address,
                             uncompressed_to_compressed_pubkey,
                             wif_to_raw_private_key, is_uncompressed_public_key, is_compressed_public_key)
from btccli.utils import is_valid_hex_str

@dataclass
class BitcoinKeys:
    wif_key: str
    """WIF Key. Electrum private key. Prefix is 'p2wpkh:[LK]. """

    priv_key_raw: str
    """Raw hex encoded private key. 64 hex characters"""

    pub_key_raw: str
    """Raw uncompressed public key. Starts with 04. 130 hex characters"""

    comp_pub_key: str
    """Compressed Public Key. Starts with 02 or 03. 66 hex characters"""

    addr_legacy: str
    """Legacy (P2PKH) Address. Starts with a 1"""

    addr_wrapped_segwit: str
    """Wrapped SegWit Address (P2SH-P2WPKH). Starts with a 3"""

    addr_segwit: str
    """Native Segwit (Bech32) Address. Starts with bc1q"""

    addr_taproot: str
    """Taproot (Bech32 bc1p...) Address"""
    
    def has_priv_key(self) -> bool:
        if self.wif_key or self.priv_key_raw:
            return True
        return False

    def __str__(self) -> str:
        """Pretty print Bitcoin key information, omitting private keys if not present"""
        parts = ["🔑 Bitcoin Key Info:", "---------------------------"]

        # Only print private keys if present
        if self.has_priv_key():
            parts.append(f"📌 Electrum WIF Key: {self.wif_key}")
            parts.append(f"🔒 Private Key (Raw): {self.priv_key_raw}")

        # Public keys (always shown)
        parts.append(f"🔓 Public Key (Uncompressed): {self.pub_key_raw}")
        parts.append(f"🔹 Public Key (Compressed): {self.comp_pub_key}")

        # Addresses (always shown)
        parts.append(f"🏛️ Legacy Address (P2PKH): {self.addr_legacy}")
        parts.append(f"📦 Wrapped SegWit (P2SH-P2WPKH): {self.addr_wrapped_segwit}")
        parts.append(f"⚡ Native SegWit (Bech32): {self.addr_segwit}")
        parts.append(f"🌱 Taproot Address (Bech32 bc1p...): {self.addr_taproot}")

        return "\n".join(parts)
    
    def validate(self, known_electrum_address : str | None = None):
        if self.wif_key:
            wif = self.wif_key[7:] if self.wif_key.startswith('p2wpkh:') else self.wif_key
            assert self.priv_key_raw == wif_to_raw_private_key(wif)
            assert wif == private_key_to_wif(self.priv_key_raw)
            assert self.pub_key_raw == private_key_to_public_key(self.priv_key_raw)

        assert is_uncompressed_public_key(self.pub_key_raw)
        assert is_compressed_public_key(self.comp_pub_key)

        assert self.comp_pub_key == uncompressed_to_compressed_pubkey(self.pub_key_raw)
        assert self.pub_key_raw == compressed_to_uncompressed_pubkey(self.comp_pub_key)

        assert self.addr_legacy == uncomp_public_key_to_legacy_address(self.pub_key_raw)
        assert self.addr_wrapped_segwit == comp_public_key_to_wrapped_segwit_address(self.comp_pub_key)
        assert self.addr_segwit == comp_public_key_to_segwit_address(self.comp_pub_key)
        assert self.addr_taproot == comp_public_key_to_taproot_address(self.comp_pub_key)

        if known_electrum_address:
            assert known_electrum_address == self.addr_segwit
        
        return self
            

def make_bitcoin_keyset(key : str | bytes, known_electrum_addr : str | None = None) -> BitcoinKeys:
    key = bytes.hex(key) if isinstance(key, bytes) else key

    # is it an elecrum wif key already
    if _is_wif(key):
        return _from_priv_key(key, None).validate(known_electrum_addr)
    
    ln = len(key)
    if ln == 64 and is_valid_hex_str(key):
        return _from_priv_key(None, key).validate(known_electrum_addr)
    
    return _from_pub_key(key).validate(known_electrum_addr)

        
def _from_priv_key(wif_key = None, raw_key = None):
    if wif_key is None and raw_key is None:
        raise ValueError("Cannot have both wif_key and raw_key empty when trying to create a BitcoinKeys from a private key")
    
    if not raw_key:
        raw_key = wif_to_raw_private_key(wif_key)
    if not wif_key:
        wif_key = private_key_to_wif(raw_key)
    return _from_pub_key(private_key_to_public_key(raw_key), wif_key, raw_key)

def _from_pub_key(public_key : str, wif_key : str | None, raw_key : str | None) -> BitcoinKeys:
    if not is_valid_hex_str(public_key):
        raise ValueError(f"Given public key {public_key} is not a hex string")
    ln = len(public_key)

    if ln == 130 and public_key.startswith('04'):
        raw_pub_key = public_key
        comp_pub_key = uncompressed_to_compressed_pubkey(public_key)
    
    elif ln == 66 and (public_key.startswith('02') or public_key.startswith('03')):
        comp_pub_key = public_key
        raw_pub_key = compressed_to_uncompressed_pubkey(public_key)

    else:
        raise ValueError(f"Unrecognized public key format {public_key}")

    return BitcoinKeys(
        wif_key=wif_key,
        priv_key_raw=raw_key,
        pub_key_raw=raw_pub_key,
        comp_pub_key=comp_pub_key,
        addr_legacy=uncomp_public_key_to_legacy_address(raw_pub_key),
        addr_wrapped_segwit=comp_public_key_to_wrapped_segwit_address(comp_pub_key),
        addr_segwit=comp_public_key_to_segwit_address(comp_pub_key),
        addr_taproot=comp_public_key_to_taproot_address(comp_pub_key))

def _is_wif(key : str) -> bool:
    if key.startswith('p2wpkh:'):
        return True
    
    if key.startswith('L') or key.startswith('K') and len(key) == 52:
        return True
    
    return False