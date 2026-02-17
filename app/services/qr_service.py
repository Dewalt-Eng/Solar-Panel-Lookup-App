import qrcode
import io


def generate_qr_image(url: str):
    qr = qrcode.make(url)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
