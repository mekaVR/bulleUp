import csv
import re
from django.core.management.base import BaseCommand
from bdtheque.models import ComicBook, Author, ComicBookAuthor

ROLE_MAP = {
    "auteur": ["Auteur", "Auteur + illustrateur", "Texte et illustration", "Scénariste et dessinateur"],
    "dessinateur": ["Illustrateur", "illustration de"],
    "scénariste": ["Scénario", "Scénariste","Texte de"],
}

IGNORED_ROLES = ["Traducteur", "Postface", "Préface", "Éditeur", "Direction de publication"]

class Command(BaseCommand):
    help = "Importe les auteurs depuis un fichier CSV et les lie aux BD avec le bon rôle"

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            help='Chemin vers le fichier CSV',
            required=True,
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row:
                    continue

                cleaned_row = {k.strip(): v for k, v in row.items()}
                ean = cleaned_row.get("ean")
                authors_str = cleaned_row.get("authors")

                if not ean or not authors_str:
                    continue

                try:
                    comic_book = ComicBook.objects.get(ean=ean)
                except ComicBook.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"BD avec EAN {ean} non trouvée"))
                    continue

                authors = self.extract_authors(authors_str)
                if not authors:
                    continue

                for name, role in authors:
                    full_name = name.strip()
                    name_parts = full_name.split()
                    first_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else None
                    last_name = name_parts[-1] if len(name_parts) > 1 else full_name

                    author, _ = Author.objects.get_or_create(
                        first_name=first_name,
                        last_name=last_name
                    )

                    relation, created = ComicBookAuthor.objects.get_or_create(
                        comic_book=comic_book,
                        author=author,
                        role=role
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Ajouté: {author} -> {comic_book.title} ({role})"))
                    else:
                        self.stdout.write(f"Déjà existant: {author} -> {comic_book.title} ({role})")

    def extract_authors(self, authors_str):
        result = []
        entries = [entry.strip() for entry in authors_str.split(",")]
        for entry in entries:
            match = re.match(r"(.+?) \((.*?)\)", entry)
            if match:
                name, role = match.groups()
                role_clean = role.strip().lower()
                if role in IGNORED_ROLES:
                    continue
                for key, values in ROLE_MAP.items():
                    if any(val.lower() == role_clean for val in values):
                        result.append((name.strip(), key))
                        break
        return result