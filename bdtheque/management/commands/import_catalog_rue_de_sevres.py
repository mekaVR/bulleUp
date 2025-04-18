import csv
import os
from django.core.files import File
from datetime import datetime

from django.core.management.base import BaseCommand
from bdtheque.models import ComicBook

class Command(BaseCommand):
    help = "Importe le catalogue de l'éditeur Rue de Sèvres depuis un document CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Chemin vers le fichier CSV'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        base_dir = os.path.dirname(csv_file)
        images_dir = os.path.join(base_dir, 'images')
        self.stdout.write(self.style.NOTICE(f"📂 Lecture du fichier : {csv_file}"))

        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                imported_count = 0
                for row in reader:
                    # 2. Parser la date au format jour/mois/année
                    date_obj = datetime.strptime(row['publication_date'], "%d/%m/%Y")
                    # 3. Reformater en année-mois-jour
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    title = row['title']
                    ean = row['ean']
                    publication_date = formatted_date
                    summary = row['summary']
                    book_format = row['book_format']
                    cover_image_filename = row['cover_image']

                    image_path = os.path.join(images_dir, cover_image_filename)

                    if not os.path.exists(image_path):
                        self.stdout.write(self.style.WARNING(f"❓ Image introuvable : {image_path}"))
                        continue

                    comic_book, created = ComicBook.objects.get_or_create(
                        ean=ean,
                        defaults={
                            'title': title,
                            'publication_date': publication_date,
                            'summary': summary,
                            'book_format': book_format,
                        }
                    )

                    # S'il a été créé et qu'une image est définie
                    if created:
                        if cover_image_filename:
                            image_path = os.path.join(images_dir, cover_image_filename)
                            if os.path.exists(image_path):
                                with open(image_path, 'rb') as img_file:
                                    comic_book.cover_image.save(cover_image_filename, File(img_file), save=True)
                            else:
                                self.stdout.write(self.style.WARNING(f"❓ Image non trouvée pour : {title}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"📭 Pas d’image pour : {title}"))

                        imported_count += 1
                        self.stdout.write(self.style.SUCCESS(f"✅ Ajouté : {title}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ Déjà existant : {title}"))


                self.stdout.write(self.style.SUCCESS(f"📚 {imported_count} bandes dessinées importées depuis {csv_file}"))

        except Exception as error:
            self.stderr.write(self.style.ERROR(f"❌ Erreur de lecture du CSV : {error}"))
