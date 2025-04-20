from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import *
from authentication.models import User


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


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_name = serializers.SerializerMethodField()
    comic_book_title = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_user_name(self, obj):
        return f"{obj.user}"

    def get_comic_book_title(self, obj):
        return f"{obj.comic_book.title}"


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class UserDetailSerializer(serializers.ModelSerializer):
    collection = UserCollectionSerializer(source='usercollection_set', many=True, read_only=True)
    wishlist = UserWishListSerializer(source='userwishlist_set', many=True, read_only=True)
    follows = FollowedUserSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(source='review_set', many=True, read_only=True)
    loans = LoanSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'birth_date', 'follows', 'collection', 'wishlist', 'reviews', 'loans']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class PublisherMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'profile_picture']


class ComicBookForAuthorDetailSerializer(serializers.ModelSerializer):
    comic_book_id = serializers.PrimaryKeyRelatedField(queryset=ComicBook.objects.all())
    comic_book_title = serializers.SerializerMethodField()

    class Meta:
        model = ComicBookAuthor
        fields = ['comic_book_id', 'comic_book_title']

    def get_comic_book_title(self, obj):
        return obj.comic_book.title


class ComicBookAuthorSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ComicBookAuthor
        fields = ['author_id', 'author_name', 'role']

    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}" if obj.author.first_name else None


class AuthorListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'author_name', 'profile_picture']

    def get_author_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class AuthorDetailSerializer(serializers.ModelSerializer):
    comic_book = ComicBookForAuthorDetailSerializer(source='comicbookauthor_set', many=True, read_only=True)

    class Meta:
        model = Author
        fields = '__all__'


class ComicBookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComicBook
        fields = ['id', 'title', 'series', 'volume', 'cover_image']


class ComicBookDetailSerializer(serializers.ModelSerializer):
    authors = ComicBookAuthorSerializer(source='comicbookauthor_set', many=True, read_only=True)
    publisher = PublisherMiniSerializer(read_only=True)
    reviews = ReviewSerializer(read_only=True,  many=True)

    class Meta:
        model = ComicBook
        fields = '__all__'
