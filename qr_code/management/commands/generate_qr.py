# your_app/management/commands/generate_qr.py
from django.core.management.base import BaseCommand
import qrcode

# Dummy table list, ya aap database se fetch kar sakte hain
TABLES = [1, 2, 3, 4, 5]

class Command(BaseCommand):
    help = 'Generate QR codes for all tables'

    def handle(self, *args, **kwargs):
        for table_id in TABLES:
            url = f"http://127.0.0.1:8000/qr-scan?table={table_id}"
            img = qrcode.make(url)
            img.save(f"table_{table_id}.png")
            self.stdout.write(self.style.SUCCESS(f'QR code generated for table {table_id}'))
