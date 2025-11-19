import re
from urllib.parse import urlencode
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from bdtheque.serializers import UserCollectionSerializer, UserWishListSerializer, ReviewSerializer
from ..models import *

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


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer pour demander une réinitialisation de mot de passe.
    Envoie un email avec un lien de réinitialisation.
    """
    email = serializers.EmailField(required=True)
    redirect_uri = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        """Vérifie que l'email existe dans la base de données"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun compte n'est associé à cet e-mail.")
        return value

    def save(self):
        """
        Génère le token de réinitialisation et envoie l'email
        """
        email = self.validated_data['email']
        redirect_uri = self.validated_data.get('redirect_uri', '')
        user = User.objects.get(email=email)

        # Générer le token de réinitialisation
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)

        # Encoder l'ID de l'utilisateur en base64
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construire le lien de réinitialisation
        # Utilise reverse() pour générer l'URL de la vue template Django
        reset_path = reverse('password-reset-form', kwargs={'uid': uid, 'token': token})

        # Obtenir le domaine depuis le contexte de la requête
        request = self.context.get('request')
        if request:
            reset_link = request.build_absolute_uri(reset_path)
        else:
            # Fallback si pas de requête (par exemple dans les tests)
            reset_link = f"http://localhost:8000{reset_path}"

        # Ajouter le redirect_uri comme query parameter si fourni
        if redirect_uri:
            query_params = urlencode({'redirect_uri': redirect_uri})
            reset_link = f"{reset_link}?{query_params}"

        # Envoyer l'email
        subject = "Réinitialisation de votre mot de passe BulleUp"
        message = f"""
Bonjour {user.username},

Vous avez demandé la réinitialisation de votre mot de passe.

Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :
{reset_link}

Ce lien est valide pendant 1 heure.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet e-mail.

Cordialement,
L'équipe BulleUp
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return {'uid': uid, 'token': token}


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer pour confirmer la réinitialisation du mot de passe
    avec le token reçu par email.
    """
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        """
        Validation du mot de passe (mêmes règles que l'inscription) :
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

    def validate(self, data):
        """
        Vérifie que les deux mots de passe correspondent et que le token est valide
        """
        # Vérifier que les mots de passe correspondent
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Les mots de passe ne correspondent pas."})

        # Décoder l'UID
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Lien de réinitialisation invalide."})

        # Vérifier la validité du token
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({"token": "Le lien de réinitialisation est expiré ou invalide."})

        data['user'] = user
        return data

    def save(self):
        """
        Change le mot de passe de l'utilisateur
        """
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
