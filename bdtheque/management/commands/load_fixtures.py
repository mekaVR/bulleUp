from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.db.models import Count

from bdtheque.models import ComicBookAuthor, Author, Publisher

class Command(BaseCommand):
    help = 'Loads fixtures in development environment if database is empty'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.WARNING('This command should only be run in development environment'))
            return

        # Check if database is empty
        total_comic_book = ComicBookAuthor.objects.count()
        total_authors = Author.objects.count()
        total_publishers = Publisher.objects.count()

        if total_comic_book == 0 and total_authors == 0 and total_publishers == 0:
            self.stdout.write('Loading fixtures...')
            fixtures = [
                'publishers',
                'authors',
                'comic_books',
                'comic_book_authors'
            ]
            
            for fixture in fixtures:
                try:
                    call_command('loaddata', fixture)
                    self.stdout.write(self.style.SUCCESS(f'Successfully loaded {fixture}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error loading {fixture}: {str(e)}'))
        else:
            self.stdout.write(self.style.WARNING('Database is not empty. Skipping fixtures loading.')) 