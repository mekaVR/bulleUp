from django.core.management import BaseCommand

from bdtheque.models import ComicBook, Publisher


class Command(BaseCommand):
    help = "Ajout de l'éditeur rue de sevres a toutes les bd"

    def handle(self, *args, **options):
        comic_books = ComicBook.objects.all()
        publisher_rds = Publisher.objects.get(pk=15)

        for comic in comic_books:
            try:
                comic.publisher = publisher_rds
                comic.save()
                self.stdout.write(self.style.NOTICE(f'ajout de l éditeur a la bd {comic}'))
                #self.stdout.write(self.style.NOTICE(f'{publisher_rds}'))
            except Exception as error:
                self.stdout.write(self.style.ERROR(f'Error loading {error}'))

        self.stdout.write(self.style.SUCCESS(f'toute les bd ont été set comme il faut'))
