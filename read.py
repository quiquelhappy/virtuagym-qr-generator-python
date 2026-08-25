import argparse
import base64
import hashlib
import json
from typing import Optional

import cv2
from Crypto.Cipher import AES

# ----------------------------
# Exact equivalents of CryptLib (mirrors gen.py)
# ----------------------------

def derive_aes_key(key_string: str) -> bytes:
    sha = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
    return sha[:32].encode("utf-8")

def pkcs5_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if not (1 <= pad_len <= 16) or data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid PKCS5 padding (wrong superclub_id / key, or corrupted data)")
    return data[:-pad_len]

# ----------------------------
# QR payload decryption
# ----------------------------

def decrypt_with_superclub_id(ciphertext: bytes, superclub_id: int) -> dict:
    key_number = ((65 + superclub_id) * 754 * superclub_id) + 9476221
    aes_key = derive_aes_key(str(key_number))

    # The IV used at encryption time is never transmitted, but in AES-CBC the IV
    # only affects the first decrypted block. Block 0 is always the random 16-char
    # "prefix" (discarded), so decrypting with an arbitrary IV still recovers the
    # real JSON payload starting at block 1 intact.
    iv = b"\x00" * 16
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    plaintext = pkcs5_unpad(cipher.decrypt(ciphertext))

    json_payload = plaintext[16:]  # drop the (corrupted) 16-byte prefix block
    return json.loads(json_payload.decode("utf-8"))

def brute_force_superclub_id(ciphertext: bytes, max_id: int) -> tuple[int, dict]:
    for superclub_id in range(max_id + 1):
        try:
            payload = decrypt_with_superclub_id(ciphertext, superclub_id)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        return payload, superclub_id
    raise ValueError(f"No superclub_id in range 0..{max_id} decrypted this QR")

def decrypt_vg_qr(qr_string: str, superclub_id: Optional[int], brute_force_max: int) -> tuple[dict, int]:
    if qr_string.startswith("vg_checkin_qr="):
        qr_string = qr_string[len("vg_checkin_qr="):]

    ciphertext = base64.b64decode(qr_string)

    if superclub_id is not None:
        return decrypt_with_superclub_id(ciphertext, superclub_id), superclub_id
    return brute_force_superclub_id(ciphertext, brute_force_max)

def read_qr_from_image(path: str) -> str:
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    if not data:
        raise ValueError(f"No QR code detected in image: {path}")
    return data

# ----------------------------
# Command-line interface
# ----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decrypt Virtuagym check-in QR codes.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--image", type=str, help="Path to a QR code PNG/image to read")
    source.add_argument("--string", type=str, help="Raw QR string (with or without 'vg_checkin_qr=' prefix)")
    parser.add_argument(
        "--superclub_id", type=int, default=None,
        help="Superclub ID used to derive the AES key. If omitted, brute-forces it (0..--brute_force_max)."
    )
    parser.add_argument(
        "--brute_force_max", type=int, default=200_000,
        help="Upper bound to brute-force superclub_id up to, when --superclub_id is not given (default: 200000)"
    )

    args = parser.parse_args()

    qr_string = read_qr_from_image(args.image) if args.image else args.string

    payload, superclub_id = decrypt_vg_qr(qr_string, args.superclub_id, args.brute_force_max)

    if args.superclub_id is None:
        print(f"superclub_id:   {superclub_id} (brute-forced)")
    print(f"timestamp:      {payload.get('timestamp')}")
    print(f"vg_member_id:   {payload.get('vg_member_id')}")
    print(f"club_member_id: {payload.get('club_member_id')}")
