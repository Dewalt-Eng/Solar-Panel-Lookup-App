import qrcode
from PIL import Image
import io
import os


def generate_qr_image(url: str):

    # High error correction because we overlay a logo
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Brand blue QR
    img = qr.make_image(
        fill_color="#008AD1",   # Brand primary blue
        back_color="white"
    ).convert("RGB")

    qr_width, qr_height = img.size

    # Load branded square logo
    logo_path = os.path.join("app", "static", "brand", "logo_square_128.png")
    logo = Image.open(logo_path).convert("RGBA")

    # Resize logo safely (important for scan reliability)
    logo_size = qr_width // 6   # 20% of QR width
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    # Calculate center position
    pos = (
        (qr_width - logo_size) // 2,
        (qr_height - logo_size) // 2
    )

    # Create white background for logo to improve scan contrast
    white_bg = Image.new("RGBA", (logo_size, logo_size), "white")
    img.paste(white_bg, pos)

    # Paste logo on top
    img.paste(logo, pos, mask=logo)

    # Save to memory buffer (NOT filesystem)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

