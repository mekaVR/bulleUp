from django.db import models, transaction
from django.contrib.auth.models import AbstractUser

from bdtheque.models import ComicBook, UserCollection, UserWishlist, Loan, Author, Publisher, AuthorFollow, \
    PublisherFollow


class User(AbstractUser):
    avatar = models.ImageField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    follows = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    collection = models.ManyToManyField(ComicBook, through=UserCollection, related_name='collection')
    wishlist =  models.ManyToManyField(ComicBook, through=UserWishlist, related_name='wishlist')
    authors_follow = models.ManyToManyField(Author, through=AuthorFollow, related_name='authors_follow')
    publisher_follow = models.ManyToManyField(Publisher, through=PublisherFollow, related_name='publisher_follow')

    def __str__(self):
        return self.username

    def _validate_following(self, user_to_follow):
        if self.pk == user_to_follow.pk:
            raise ValueError("Vous ne pouvez pas vous suivre vous-même")
        if self.follows.filter(pk=user_to_follow.pk).exists():
            raise ValueError("Vous suivez déjà cet utilisateur")

    def _validate_follow_author(self, author_id):
        if self.authors_follow.filter(pk=author_id).exists():
            raise ValueError("Vous suivez déjà cet auteur")

    def _validate_follow_publisher(self, publisher_id):
        if self.publisher_follow.filter(pk=publisher_id).exists():
            raise ValueError("Vous suivez déjà cet éditeur")

    def _validate_loan(self, comic_book):
        if self.loans.filter(comic_book=comic_book.pk).exists():
            raise ValueError("Vous avez déjà préte cette bande déssiné")

    @transaction.atomic
    def add_follower(self, user_to_follow):
        self._validate_following(user_to_follow)
        self.follows.add(user_to_follow)

    @transaction.atomic
    def remove_follower(self, user_to_follow):
        self.follows.remove(user_to_follow)

    @transaction.atomic
    def add_comic_in_collection(self, comic_to_add):
        self.collection.add(comic_to_add)

    @transaction.atomic
    def remove_comic_in_collection(self, comic_to_remove):
        self.collection.remove(comic_to_remove)

    @transaction.atomic
    def add_comic_in_wishlist(self, comic_to_add):
        self.wishlist.add(comic_to_add)

    @transaction.atomic
    def remove_comic_in_wishlist(self, comic_to_remove):
        self.wishlist.remove(comic_to_remove)

    @transaction.atomic
    def loan_comic_book(self, payload):
        self._validate_loan(payload['comic_book'])
        Loan.objects.create(**payload)

    @transaction.atomic
    def follow_author(self, author_to_follow):
        self._validate_follow_author(author_to_follow)
        self.authors_follow.add(author_to_follow)

    @transaction.atomic
    def unfollow_author(self, author_to_unfollow):
        self.authors_follow.remove(author_to_unfollow)

    @transaction.atomic
    def follow_publisher(self, publisher_to_follow):
        self._validate_follow_publisher(publisher_to_follow)
        self.publisher_follow.add(publisher_to_follow)

    @transaction.atomic
    def unfollow_publisher(self, publisher_to_unfollow):
        self.publisher_follow.remove(publisher_to_unfollow)