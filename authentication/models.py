from django.db import models, transaction
from django.contrib.auth.models import AbstractUser

from bdtheque.models import ComicBook, UserCollection, UserWishlist, Loan


class User(AbstractUser):
    avatar = models.ImageField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    follows = models.ManyToManyField('self', symmetrical=False)
    collection = models.ManyToManyField(ComicBook, through=UserCollection, related_name='collection')
    wishlist =  models.ManyToManyField(ComicBook, through=UserWishlist, related_name='wishlist')

    def __str__(self):
        return self.username

    def _validate_following(self, user_to_follow):
        if self.pk == user_to_follow.pk:
            raise ValueError("Vous ne pouvez pas vous suivre vous-même")
        if self.follows.filter(pk=user_to_follow.pk).exists():
            raise ValueError("Vous suivez déjà cet utilisateur")

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
