import segno

def url_to_qrcode_print(url: str) -> None:
    print(f"Generate QR code for URL:")
    qr = segno.make(f"http://{url}")
    qr.terminal(compact=True)
