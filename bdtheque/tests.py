from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse, reverse_lazy
from .models import ComicBook, Author, Publisher, ComicBookAuthor

class ComicBookAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.publisher = Publisher.objects.create(name="Kana")
        cls.publisher_2 = Publisher.objects.create(name="Casterman")

        cls.author = Author.objects.create(first_name="Katsuhiro", last_name="Otomo")
        cls.author_2 = Author.objects.create(first_name="Toriyama", last_name="Akira")

        cls.comic_book = ComicBook.objects.create(
        title="Akira",
        ean="9782344012747",
        genre="science-fiction",
        category="mangas",
        series="Akira",
        volume= 1,
        publication_date="1982-12-20",
        rating="4.50",
        book_format="Broché",
        summary="Un classique du cyberpunk.",
        publisher=cls.publisher,
        )
        cls.comic_book_2 = ComicBook.objects.create(
        title="Gunmm",
        ean="9782344012743",
        genre="science-fiction",
        category="mangas",
        series="Gunmm",
        volume= 1,
        publication_date="1982-12-20",
        rating="4.50",
        book_format="Broché",
        summary="Un classique du cyberpunk.",
        publisher=cls.publisher_2,
        )

        ComicBookAuthor.objects.create(
            comic_book=cls.comic_book,
            authors=cls.author,
            role='author'
        )


    def get_comic_book_list_data(self, comic_books):
        return [
            {
                "id": comic_book.pk,
                "title": comic_book.title,
                "series": comic_book.series,
                "volume": comic_book.volume,
                "cover_image": None,
            } for comic_book in comic_books
        ]

    def get_comic_book_detail_data(self, comic_book, author):
        authors_data = [
            {'author_name': f'{author.first_name} {author.last_name}', 'role': cb_author.role}
            for cb_author in ComicBookAuthor.objects.filter(comic_book=comic_book)
            for author in Author.objects.filter(id=cb_author.authors.id)
        ]

        return {
                "id": comic_book.id,
                "title": comic_book.title,
                "ean": comic_book.ean,
                "genre": comic_book.genre,
                "category": comic_book.category,
                "series": comic_book.series,
                "volume": comic_book.volume,
                "publication_date": comic_book.publication_date,
                "rating": comic_book.rating,
                "book_format": comic_book.book_format,
                "summary": comic_book.summary,
                "cover_image": None,
                "publisher": {
                    "id": comic_book.publisher.id,
                    "name": comic_book.publisher.name,
                },
                "authors": authors_data
            }


class TestComicBook(ComicBookAPITestCase):

    url = reverse_lazy('comic-book-list')

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_comic_book_list_data([self.comic_book, self.comic_book_2]), response.json()['results'])

    def test_detail(self):
        response = self.client.get(reverse('comic-book-detail', kwargs={'pk': self.comic_book.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_comic_book_detail_data(self.comic_book, self.author), response.json())