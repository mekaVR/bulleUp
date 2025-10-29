import re
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from bdtheque.serializers import UserCollectionSerializer, UserWishListSerializer, ReviewSerializer
from .models import *

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all(), message="Un compte existe déjà avec cet e-mail")],
            )

    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", 'password', "tokens"]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        """
        Validation du mot de passe :
        - minimum 8 caractères
        - au moins une majuscule
        - au moins une minuscule
        - au moins un chiffre
        """
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        return value

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data['email'], username=validated_data['username'], password=validated_data['password'])
        user.save()
        return user
