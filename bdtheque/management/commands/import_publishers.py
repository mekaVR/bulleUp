import pandas as pd
from django.core.management.base import BaseCommand
from bdtheque.models import Publisher  # Remplace "bd" par le nom de ton app

class Command(BaseCommand):
    help = "Importe les éditeurs de bande dessinée depuis un fichier CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Chemin vers le fichier CSV à importer.'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        self.stdout.write(self.style.NOTICE(f"📂 Lecture du fichier : {file_path}"))

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Erreur de lecture du CSV : {e}"))
            return

        for _, row in df.iterrows():
            name = row['name'].strip()
            description = row.get('description', '').strip() or None
            social_links = [row['social_links']] if pd.notna(row['social_links']) else []

            publisher, created = Publisher.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'social_links': social_links
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Ajouté : {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Déjà existant : {name}"))
