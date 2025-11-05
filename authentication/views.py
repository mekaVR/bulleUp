from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View

from .models import *
from .forms import PasswordResetConfirmForm
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.serializers import (
    UserRegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)

    @require_http_methods(["GET"])
    def get_user_exist(request):
        username = request.GET.get('username')
        if not username:
            return JsonResponse({"error": "Le paramètre username est requis"}, status=400)

        exists = User.objects.filter(username=username).exists()
        message = "Ce nom d'utilisateur existe déjà" if exists else "Ce nom d'utilisateur est disponible"
        return JsonResponse({"exists": exists, "message": message})


class PasswordResetRequestView(generics.GenericAPIView):
    """
    POST /password-reset/

    Endpoint pour demander une réinitialisation de mot de passe.
    Envoie un email avec un lien de réinitialisation si l'email existe.

    Body:
    {
        "email": "user@example.com"
    }

    Response:
    {
        "message": "Un e-mail de réinitialisation a été envoyé."
    }
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Un e-mail de réinitialisation a été envoyé."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    POST /password-reset-confirm/

    Endpoint pour confirmer la réinitialisation du mot de passe
    avec le token reçu par email.

    Body:
    {
        "uid": "MQ",
        "token": "abc123-def456",
        "new_password": "NewPass123",
        "new_password_confirm": "NewPass123"
    }

    Response:
    {
        "message": "Votre mot de passe a été réinitialisé avec succès."
    }
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Votre mot de passe a été réinitialisé avec succès."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetFormView(View):
    """
    Vue Django pour afficher le formulaire HTML de réinitialisation de mot de passe.

    GET /reset-password/<uid>/<token>/
    Affiche le formulaire de réinitialisation

    POST /reset-password/<uid>/<token>/
    Traite le formulaire et change le mot de passe
    """
    template_name = 'authentication/password_reset_form.html'
    success_template = 'authentication/password_reset_success.html'

    def get(self, request, uid, token):
        """
        Affiche le formulaire de réinitialisation
        Accepte un paramètre redirect_uri pour rediriger vers l'app mobile
        """
        form = PasswordResetConfirmForm(uid=uid, token=token)
        redirect_uri = request.GET.get('redirect_uri', '')
        return render(request, self.template_name, {
            'form': form,
            'redirect_uri': redirect_uri
        })

    def post(self, request, uid, token):
        """
        Traite le formulaire et change le mot de passe
        """
        form = PasswordResetConfirmForm(uid=uid, token=token, data=request.POST)
        redirect_uri = request.POST.get('redirect_uri', request.GET.get('redirect_uri', ''))

        if form.is_valid():
            # Sauvegarder le nouveau mot de passe
            form.save()
            # Rediriger vers la page de succès avec le redirect_uri
            return render(request, self.success_template, {
                'redirect_uri': redirect_uri
            })

        # Si le formulaire n'est pas valide, réafficher avec les erreurs
        return render(request, self.template_name, {
            'form': form,
            'redirect_uri': redirect_uri
        })