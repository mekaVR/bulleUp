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
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar']


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
        fields = ['id', 'username', 'first_name', 'last_name']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar', 'bio']


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
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'birth_date', 'bio', 'follows', 'collection', 'wishlist', 'reviews', 'loans', 'authors_follow', 'publisher_follow']


class UserProfileSerializer(serializers.ModelSerializer):
    collection = UserCollectionSerializer(source='usercollection_set', many=True, read_only=True)
    wishlist = UserWishListSerializer(source='userwishlist_set', many=True, read_only=True)
    authors_follow = AuthorFollowSerializer(source='authorfollow_set', many=True, read_only=True)
    publisher_follow = PublisherFollowSerializer(source='publisherfollow_set', many=True, read_only=True)
    follows = FollowedUserSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(source='review_set', many=True, read_only=True)
    loans = LoanSerializer(many=True, read_only=True)

    total_collection = serializers.SerializerMethodField()
    total_wishlist = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'avatar',
            'birth_date',
            'bio',

            'collection',
            'wishlist',
            'reviews',
            'loans',
            'follows',
            'authors_follow',
            'publisher_follow',

            'total_collection',
            'total_wishlist',
            'total_reviews',
        ]
        read_only_fields = fields

    def get_total_collection(self, obj):
        return obj.usercollection_set.count()

    def get_total_wishlist(self, obj):
        return obj.userwishlist_set.count()

    def get_total_reviews(self, obj):
        return obj.review_set.count()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'avatar',
            'birth_date',
            'bio',
        ]

    def validate_email(self, value):
        user = self.context['request'].user

        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "Cet email est déjà utilisé par un autre utilisateur."
            )

        return value

    def validate_birth_date(self, value):
        from datetime import date, timedelta

        if value:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

            if value > today:
                raise serializers.ValidationError(
                    "La date de naissance ne peut pas être dans le futur."
                )

        return value
