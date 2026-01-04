import argparse
import base64
import hashlib
import json
import secrets
import time
from typing import Optional
from Crypto.Cipher import AES
import qrcode

# ----------------------------
# Exact equivalents of CryptLib
# ----------------------------

def random_hex_16():
    return secrets.token_hex(8)[:16]  # 16 hex chars

def derive_aes_key(key_string: str) -> bytes:
    sha = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
    return sha[:32].encode("utf-8")

def pkcs5_pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

# ----------------------------
# QR payload encryption
# ----------------------------

def generate_vg_qr(
    vg_member_id: int,
    superclub_id: int,
    club_member_id: Optional[str] = None,
    timestamp_ms: Optional[int] = None,
):
    if timestamp_ms is None:
        timestamp_ms = int(time.time() * 1000)

    payload = {
        "timestamp": timestamp_ms,
        "vg_member_id": vg_member_id,
    }

    if club_member_id is not None:
        payload["club_member_id"] = club_member_id

    json_payload = json.dumps(payload, separators=(",", ":"))

    key_number = ((65 + superclub_id) * 754 * superclub_id) + 9476221
    aes_key = derive_aes_key(str(key_number))

    prefix = random_hex_16()
    iv_string = random_hex_16()
    iv = iv_string.encode("utf-8")[:16]

    plaintext = pkcs5_pad((prefix + json_payload).encode("utf-8"))
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(plaintext)

    qr_data = base64.b64encode(ciphertext).decode("utf-8")
    return f"vg_checkin_qr={qr_data}"

# ----------------------------
# Command-line interface
# ----------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Virtuagym QR codes.")
    parser.add_argument("--vg_member_id", type=int, required=True, help="VG member ID")
    parser.add_argument("--superclub_id", type=int, required=True, help="Superclub ID")
    parser.add_argument("--club_member_id", type=str, default=None, help="Club member ID (optional)")
    parser.add_argument("--qr", action="store_true", help="Render the final string as an ASCII QR to stdout")
    parser.add_argument("--qr-image", type=str, default=None, help="Path to save PNG QR image")

    args = parser.parse_args()

    qr = generate_vg_qr(
        vg_member_id=args.vg_member_id,
        superclub_id=args.superclub_id,
        club_member_id=args.club_member_id
    )

    # If requested, render QR to terminal as ASCII
    if args.qr:
        qr_obj = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=2
        )
        qr_obj.add_data(qr)
        qr_obj.make(fit=True)
        matrix = qr_obj.get_matrix()
        for row in matrix:
            print("".join("██" if cell else "  " for cell in row))
    else:
        print(qr)

    # If requested, save a PNG image of the QR code
    if args.qr_image:
        qr_obj = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=2
        )
        qr_obj.add_data(qr)
        qr_obj.make(fit=True)
        img = qr_obj.make_image(fill_color="black", back_color="white")
        img.save(args.qr_image)
