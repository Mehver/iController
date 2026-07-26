# SPDX-FileCopyrightText: 2024 Mehver (https://github.com/Mehver)
# SPDX-License-Identifier: BSD-3-Clause

import segno

def url_to_qrcode_print(url: str) -> None:
    print(f"Generate QR code for URL:")
    qr = segno.make(f"http://{url}")
    qr.terminal(compact=True)
