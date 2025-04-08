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
    #user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Review
        #fields = ['id', 'rating', 'summary', 'publication_date', 'user', 'user_detail', 'work']
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