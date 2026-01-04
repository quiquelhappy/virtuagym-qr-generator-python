# Disclaimer
This repository is a small tool built for experimenting with Virtuagym QR payloads. Use it only where you have permission. The code is provided for research and security-hardening purposes.

# How to run
Login into your gym's website using the virtuagym software, in my case, https://<your gym slug>.virtuagym.com/
You can likely find this URL by looking for a login option inside your gym landing page or password recovery in-app.

Then, login, and get the following cookies:
- ``virtuagym_u``
- ``virtuagym_pref_club``

then, run the script with:
```
python3 gen.py --vg_member_id <VG_MEMBER_ID> --superclub_id <SUPERCLUB_ID>
```

if this doesn't work, try
```
python3 gen.py --vg_member_id <VG_MEMBER_ID> --superclub_id <SUPERCLUB_ID> --club_member_id <CLUB_MEMBER_ID>
```
I'm not sure on where to get ``your_club_member_id``, it might show up at ``https://<your gym slug>.virtuagym.com/user/<your account slug>/settings/sportschool``

# Installation

Install the Python dependencies (recommended in a virtualenv):

```bash
pip3 install -r requirements.txt
```

# Options
By default, it shows the raw QR code data in console, but you can use:
- `--qr` : Render the generated final string as an ASCII QR code in the terminal.
- `--qr-image <path>` : Save a PNG image of the QR code to `<path>`.

Both options can be combined; for example the command below prints an ASCII QR and writes `out.png`:

```bash
python3 gen.py --vg_member_id 21860781 --superclub_id 61212 --qr --qr-image out.png
```

# Output
The script prints a string like:

```
vg_checkin_qr=<base64...>
```

When `--qr` (console output) or `--qr-image` (outputs png to the specified path) are used that full string is encoded into the QR value.

# Notes
- The QR payload is produced by encrypting a small JSON payload; the resulting value is prefixed with `vg_checkin_qr=`.