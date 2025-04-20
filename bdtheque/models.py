from django.db import models, transaction
from django.conf import settings

class ComicBook(models.Model):

    GENRE_CHOICE = [
        ('autobiographique', 'Autobiographique'),
        ('aventure', 'Aventure'),
        ('fantasy', 'Fantasy'),
        ('guerre', 'Guerre'),
        ('horreur', 'Horreur'),
        ('science-fiction', 'Science-Fiction'),
        ('western', 'Western'),
        ('documentaire', 'Documentaire'),
        ('erotique', 'Érotique'),
        ('fantastique', 'Fantastique'),
        ('historique', 'Historique'),
        ('humoristique', 'Humoristique'),
        ('muet', 'Muet'),
        ('pedagogique', 'Pédagogique'),
        ('policier', 'Polar-Policier'),
        ('roman-graphique', 'Roman-graphique'),
        ('comic-strip', 'Comic-strip'),
        ('shonen', 'Shonen'),
        ('seinen', 'Seinen'),
        ('shojo-josei', 'Shōjo/Josei'),
        ('auteurs', 'Auteurs'),
        ('webtoon', 'Webtoon'),
    ]

    CATEGORY_CHOICES = [
        ('bd-adulte', 'BD Adulte'),
        ('bd-jeunesse', 'BD Jeunesse'),
        ('independants', 'Indépendants'),
        ('mangas', 'Mangas'),
        ('humour-bd', 'Humour BD'),
        ('comics', 'Comics'),
    ]

    title = models.CharField(max_length=255)
    cover_image = models.ImageField(blank=True, null=True)
    ean = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=50, blank=True, choices=GENRE_CHOICE, null=True)
    category = models.CharField(max_length=50, blank=True, choices=CATEGORY_CHOICES, null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    rating = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    book_format = models.CharField(max_length=50, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    publisher = models.ForeignKey('Publisher', on_delete=models.SET_NULL, null=True, blank=True)
    authors = models.ManyToManyField('Author', through='ComicBookAuthor')

    def __str__(self):
        return self.title


class Author(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)
    comic_book = models.ManyToManyField('Author', through='ComicBookAuthor')

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.last_name


class AuthorFollow(models.Model):
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)


class ComicBookAuthor(models.Model):
    ROLE_CHOICE = [
        ('auteur', 'Auteur'),
        ('scénariste', 'Scénariste'),
        ('dessinateur', 'Dessinateur'),
        ('coloriste', 'Coloriste')
    ]

    comic_book = models.ForeignKey(ComicBook, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICE)

    class Meta:
        unique_together = ('comic_book', 'author', 'role')


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class PublisherFollow(models.Model):
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])
    summary = models.TextField(blank=True, null=True)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    comic_book = models.ForeignKey(ComicBook, on_delete=models.CASCADE, related_name='reviews')
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} on {self.comic_book}"


class UserCollection(models.Model):
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    comic_book = models.ForeignKey(ComicBook, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)


class UserWishlist(models.Model):
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    comic_book = models.ForeignKey(ComicBook, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)


class Loan(models.Model):
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='loans')
    username = models.CharField(max_length=150, blank=True, null=True)
    friend = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True)
    comic_book = models.ForeignKey(ComicBook, on_delete=models.CASCADE)
    loan_date = models.DateField(auto_now_add=True)