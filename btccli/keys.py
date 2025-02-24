import hashlib

import base58
import bech32
import ecdsa
from bitcoinutils.setup import setup
from ecdsa.ecdsa import curve_secp256k1, ellipticcurve
from bitcoinutils.keys import PublicKey

from btccli.utils import is_valid_hex_str

# Set up the network; use 'mainnet' for the main Bitcoin network
setup('mainnet')

def wif_to_raw_private_key(wif_key: str) -> str:
    """
    Electrum private keys with a prefix 'p2wpkh:' and starting with a L or K.
    """
    wif_key = wif_key[7:] if wif_key.startswith('p2wpkh:') else wif_key
    decoded = base58.b58decode_check(wif_key)
    
    # Remove the first byte (prefix) and last byte (if compressed key)
    raw_key = decoded[1:-1] if len(decoded) == 34 else decoded[1:]
    
    return raw_key.hex()

def private_key_to_public_key(private_key_hex):
    private_key_bytes = bytes.fromhex(private_key_hex)

    # Use secp256k1 curve to generate the public key
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    public_key = b'\x04' + vk.to_string()  # Uncompressed public key
    return public_key.hex()

def uncompressed_to_compressed_pubkey(uncompressed_pubkey):
    if len(uncompressed_pubkey) != 130 or not uncompressed_pubkey.startswith("04"):
        raise ValueError("Invalid uncompressed public key")

    # Extract X and Y coordinates
    x = uncompressed_pubkey[2:66]  # First 32 bytes after '04'
    y = uncompressed_pubkey[66:]   # Last 32 bytes

    # Convert Y to an integer to check if even or odd
    y_int = int(y, 16)

    # Compressed key: 02 if Y is even, 03 if Y is odd
    prefix = "02" if y_int % 2 == 0 else "03"

    # Return compressed public key
    return prefix + x

def private_key_to_wif(private_key_hex):
    """Convert a 32-byte hex private key to Compressed WIF (starts with K or L)"""
    private_key_bytes = bytes.fromhex(private_key_hex)

    # Add Bitcoin mainnet prefix (0x80)
    extended_key = b'\x80' + private_key_bytes

    # Add 0x01 suffix for compressed key format
    extended_key += b'\x01'

    # Compute double SHA-256 checksum
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]

    # Append checksum and encode in Base58Check
    wif_key = base58.b58encode(extended_key + checksum).decode('utf-8')

    return wif_key

def compressed_to_uncompressed_pubkey(compressed_pubkey):
    """Convert a compressed public key (02/03 + X) to an uncompressed public key (04 + X + Y)."""
    if len(compressed_pubkey) != 66 or not (compressed_pubkey.startswith("02") or compressed_pubkey.startswith("03")):
        raise ValueError("Invalid compressed public key format")

    # Extract X coordinate
    x_hex = compressed_pubkey[2:]
    x = int(x_hex, 16)

    # Compute Y^2 = x^3 + 7 mod p
    p = curve_secp256k1.p()
    y_squared = (x**3 + 7) % p

    # Compute modular square root (Y value)
    y = pow(y_squared, (p + 1) // 4, p)  # secp256k1 specific sqrt mod p

    # Check if computed Y matches the parity given by the prefix (02 = even, 03 = odd)
    if (compressed_pubkey.startswith("02") and y % 2 != 0) or (compressed_pubkey.startswith("03") and y % 2 == 0):
        y = p - y  # Flip Y to correct parity

    # Convert to hex and return uncompressed format
    y_hex = format(y, '064x')
    return "04" + x_hex + y_hex

def uncomp_public_key_to_legacy_address(public_key_hex):
    """ Generate a legacy P2PKH Bitcoin address (starts with '1') """
    if not is_uncompressed_public_key(public_key_hex):
        raise ValueError(f"public_key_to_segwit_address expects a compressed public key but was passed {public_key_hex}")
    public_key_bytes = bytes.fromhex(public_key_hex)

    # Perform SHA-256 hashing on the public key
    sha256 = hashlib.sha256(public_key_bytes).digest()

    # Perform RIPEMD-160 hashing on the SHA-256 result
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256)
    hashed_public_key = ripemd160.digest()

    # Add network byte (0x00 for Bitcoin mainnet)
    network_byte = b'\x00' + hashed_public_key

    # Perform double SHA-256 hash for checksum
    checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]

    # Concatenate hashed public key and checksum
    address_bytes = network_byte + checksum

    # Convert to Base58 to get the final Bitcoin address
    return base58.b58encode(address_bytes).decode('utf-8')

def comp_public_key_to_wrapped_segwit_address(public_key_hex):
    """ Generate a wrapped SegWit P2SH-P2WPKH Bitcoin address (starts with '3') """
    if not is_compressed_public_key(public_key_hex):
        raise ValueError(f"comp_public_key_to_wrapped_segwit_address expects a compressed public key but was passed {public_key_hex}")
    public_key_bytes = bytes.fromhex(public_key_hex)
    sha256 = hashlib.sha256(public_key_bytes).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    segwit_script = b'\x00\x14' + ripemd160  # P2WPKH script
    sha256_script = hashlib.sha256(segwit_script).digest()
    ripemd160_script = hashlib.new('ripemd160', sha256_script).digest()
    network_byte = b'\x05' + ripemd160_script
    checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
    return base58.b58encode(network_byte + checksum).decode()

def comp_public_key_to_segwit_address(public_key_hex):
    """ Generate a native SegWit Bech32 Bitcoin address (starts with 'bc1') using the compressed public key """
    if not is_compressed_public_key(public_key_hex):
        raise ValueError(f"comp_public_key_to_segwit_address expects a compressed public key but was passed {public_key_hex}")
    
    public_key_bytes = bytes.fromhex(public_key_hex)

    # Perform SHA-256 hashing on the compressed public key
    sha256_hash = hashlib.sha256(public_key_bytes).digest()

    # Perform RIPEMD-160 hashing on the SHA-256 result
    ripemd160 = hashlib.new('ripemd160', sha256_hash).digest()

    # Convert to Bech32 address (native SegWit, bc1...)
    return bech32.encode("bc", 0, ripemd160)

def comp_public_key_to_taproot_address(public_key_hex: str) -> str:
    """Generate a Taproot (bc1p...) address from an uncompressed public key."""
    
    # Validate input
    if not is_compressed_public_key(public_key_hex):
        raise ValueError(f"comp_public_key_to_taproot_address expects a compressed public key but was passed {public_key_hex}")

    pub = PublicKey(public_key_hex)

    # Generate the Taproot address
    taproot_address = pub.get_taproot_address()

    return taproot_address.to_string()

def is_compressed_public_key(public_key : str):
    return len(public_key)== 66 and (public_key.startswith('02') or public_key.startswith('03')) and is_valid_hex_str(public_key)

def is_uncompressed_public_key(public_key : str):
    return len(public_key)== 130 and public_key.startswith('04') and is_valid_hex_str(public_key)
