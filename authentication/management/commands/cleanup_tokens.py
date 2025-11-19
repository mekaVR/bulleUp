"""
Commande Django pour nettoyer les tokens JWT expirés.

Usage:
    python manage.py cleanup_tokens [--days 30] [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class Command(BaseCommand):
    help = 'Nettoie les tokens JWT expirés et blacklistés'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7,
                          help='Supprimer les tokens expirés depuis X jours (défaut: 7)')
        parser.add_argument('--dry-run', action='store_true',
                          help='Simuler sans supprimer')

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        # Récupération des tokens à supprimer
        expired_tokens = OutstandingToken.objects.filter(expires_at__lt=cutoff_date)
        blacklisted_expired = BlacklistedToken.objects.filter(token__expires_at__lt=cutoff_date)

        expired_count = expired_tokens.count()
        blacklisted_count = blacklisted_expired.count()
        total_to_delete = expired_count + blacklisted_count

        # Affichage du résumé
        self.stdout.write(f'\n{"DRY-RUN - " if dry_run else ""}Nettoyage des tokens JWT')
        self.stdout.write(f'Tokens expirés depuis plus de {days} jours:')
        self.stdout.write(f'  • Outstanding: {expired_count}')
        self.stdout.write(f'  • Blacklisted: {blacklisted_count}')

        if total_to_delete == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ Aucun token à nettoyer\n'))
            return

        # Aperçu de quelques tokens (optionnel mais utile)
        if expired_count > 0 and not dry_run:
            self.stdout.write('\nExemples:')
            for token in expired_tokens[:3]:
                user = token.user.username if token.user else '[supprimé]'
                self.stdout.write(f'  • {token.jti[:12]}... - {user}')

        # Suppression
        if not dry_run:
            blacklisted_expired.delete()
            expired_tokens.delete()
            self.stdout.write(self.style.SUCCESS(f'\n✓ {total_to_delete} tokens supprimés\n'))
        else:
            self.stdout.write(self.style.NOTICE(f'\n→ {total_to_delete} tokens seraient supprimés\n'))