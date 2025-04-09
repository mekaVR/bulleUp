from rest_framework import serializers
from .models import *
from authentication.models import User


class UserCollectionSerializer(serializers.ModelSerializer):
    oeuvre = serializers.PrimaryKeyRelatedField(queryset=ComicBook.objects.all(), write_only=True)
    oeuvre_title = serializers.SerializerMethodField()

    class Meta:
        model = UserCollection
        fields = '__all__'

    def get_oeuvre_title(self, obj):
        return obj.oeuvre.title if obj.oeuvre else None


class UserWishListSerializer(serializers.ModelSerializer):
    oeuvre = serializers.StringRelatedField()

    class Meta:
        model = UserWishlist
        fields = '__all__'


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']


class UserDetailSerializer(serializers.ModelSerializer):
    collection = UserCollectionSerializer(source='usercollection_set', many=True, read_only=True)
    wishlist = UserWishListSerializer(source='userwishlist_set', many=True, read_only=True)
    follows = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )
    reviews = ReviewSerializer(source='review_set', many=True, read_only=True)

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
        fields = ['id', 'name']


class ComicBookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComicBook
        fields = ['id', 'title', 'series', 'volume', 'cover_image']


class ComicBookAuthorSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), write_only=True)
    author_name = serializers.SerializerMethodField()
    comic_book = serializers.StringRelatedField()

    class Meta:
        model = ComicBookAuthor
        fields = ['id', 'authors', 'author_name', 'comic_book', 'role']

    def get_author_name(self, obj):
        return f"{obj.authors.first_name} {obj.authors.last_name}" if obj.authors.first_name else None


class ComicBookAuthorMiniSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), write_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = ComicBookAuthor
        fields = ['authors', 'author_name', 'role']

    def get_author_name(self, obj):
        return f"{obj.authors.first_name} {obj.authors.last_name}" if obj.authors.first_name else None


class ComicBookDetailSerializer(serializers.ModelSerializer):
    authors = ComicBookAuthorMiniSerializer(source='comicbookauthor_set', many=True, read_only=True)
    publisher = PublisherMiniSerializer(read_only=True)

    class Meta:
        model = ComicBook
        fields = '__all__'