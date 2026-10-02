"""Gera o par de chaves VAPID das notificações push. Rode UMA vez e copie para o .env."""
import base64

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Gera VAPID_PUBLIC_KEY e VAPID_PRIVATE_KEY (notificações push)."

    def handle(self, *args, **opts):
        try:
            from cryptography.hazmat.primitives import serialization
            from py_vapid import Vapid
        except ImportError:
            raise CommandError("Instale as dependências: pip install pywebpush")
        v = Vapid()
        v.generate_keys()
        publica = v.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        privada = v.private_key.private_numbers().private_value.to_bytes(32, 'big')
        b64 = lambda b: base64.urlsafe_b64encode(b).decode().rstrip('=')
        self.stdout.write("Cole no seu arquivo .env (e NÃO compartilhe a privada):\n")
        self.stdout.write(f"VAPID_PUBLIC_KEY={b64(publica)}")
        self.stdout.write(f"VAPID_PRIVATE_KEY={b64(privada)}")
        self.stdout.write("VAPID_EMAIL=mailto:seu@email.com")
