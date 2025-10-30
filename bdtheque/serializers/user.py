from rest_framework import serializers

from authentication.models import User
from ..models import UserCollection, UserWishlist, ComicBook
from .author import AuthorFollowSerializer
from .publisher import PublisherFollowSerializer
from .review import ReviewSerializer
from .loan import LoanSerializer


class FollowedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserCollectionSerializer(serializers.ModelSerializer):
    comic_book = serializers.PrimaryKeyRelatedField(queryset=ComicBook.objects.all(), write_only=True)
    comic_book_title = serializers.SerializerMethodField()
    comic_book_id = serializers.SerializerMethodField()

    class Meta:
        model = UserCollection
        fields = ['comic_book','comic_book_title', 'comic_book_id']

    def get_comic_book_title(self, obj):
        return obj.comic_book.title if obj.comic_book else None

    def get_comic_book_id(self, obj):
        return obj.comic_book.pk


class UserWishListSerializer(serializers.ModelSerializer):
    comic_book = serializers.PrimaryKeyRelatedField(queryset=ComicBook.objects.all(), write_only=True)
    comic_book_title = serializers.SerializerMethodField()
    comic_book_id = serializers.SerializerMethodField()

    class Meta:
        model = UserWishlist
        fields = ['comic_book','comic_book_title', 'comic_book_id']

    def get_comic_book_title(self, obj):
        return obj.comic_book.title if obj.comic_book else None

    def get_comic_book_id(self, obj):
        return obj.comic_book.pk


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']


class UserDetailSerializer(serializers.ModelSerializer):
    collection = UserCollectionSerializer(source='usercollection_set', many=True, read_only=True)
    wishlist = UserWishListSerializer(source='userwishlist_set', many=True, read_only=True)
    authors_follow = AuthorFollowSerializer(source='authorfollow_set', many=True, read_only=True)
    publisher_follow = PublisherFollowSerializer(source='publisherfollow_set', many=True, read_only=True)
    follows = FollowedUserSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(source='review_set', many=True, read_only=True)
    loans = LoanSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'birth_date', 'follows', 'collection', 'wishlist', 'reviews', 'loans', 'authors_follow', 'publisher_follow']
