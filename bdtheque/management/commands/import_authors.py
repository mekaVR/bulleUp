import csv
from django.core.management.base import BaseCommand
from bdtheque.models import Author


class Command(BaseCommand):
    help = 'Importe les auteurs depuis un fichier CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Chemin vers le fichier CSV')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            imported_count = 0
            for row in reader:
                first_name = row['first_name'] or None
                last_name = row['last_name']

                author, created = Author.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name
                )

                if created:
                    imported_count += 1

        self.stdout.write(self.style.SUCCESS(f"{imported_count} auteurs importés depuis {csv_file}"))
