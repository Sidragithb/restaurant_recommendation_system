# qr/utils.py
import io, uuid, qrcode
from django.core.files.base import ContentFile

def generate_qr_code(target_url: str) -> ContentFile:
    """Return PNG image as Django ContentFile (ready for ImageField)."""
    qr = qrcode.QRCode(version=1, box_size=10, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name=f"qr_{uuid.uuid4().hex}.png")
