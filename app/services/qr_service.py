#imports used by the QR service implementation
import qrcode
from PIL import Image
import io
import os

#this code is used to implement the generation of the QR images, the styling and formatting of the images
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

    # Load logo
    logo_path = os.path.join("app", "static", "brand", "logo_square_128.png")
    logo = Image.open(logo_path).convert("RGBA")

    # Make logo slightly smaller
    logo_size = int(qr_width * 0.20)   # reduce actual logo to 20%
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    # Add generous padding
    padding = int(logo_size * 0.10)    # 10% padding
    bg_size = logo_size + (padding * 2)

    white_bg = Image.new("RGBA", (bg_size, bg_size), "white")

    # Center logo inside padded area
    white_bg.paste(logo, (padding, padding), logo)

    # Position in QR center
    pos = (
        (qr_width - bg_size) // 2,
        (qr_height - bg_size) // 2
    )

    img = img.convert("RGBA")
    img.paste(white_bg, pos, white_bg)


    # Save to memory buffer (NOT filesystem)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

