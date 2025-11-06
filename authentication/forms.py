import re
from django import forms
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .models import User


class PasswordResetConfirmForm(forms.Form):
    """
    Formulaire pour la réinitialisation du mot de passe.
    Utilisé dans la vue template pour afficher le formulaire HTML.
    """
    new_password = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nouveau mot de passe',
            'id': 'id_new_password'
        }),
        min_length=8,
        help_text='Minimum 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre'
    )

    new_password_confirm = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe',
            'id': 'id_new_password_confirm'
        }),
        min_length=8
    )

    def __init__(self, uid, token, *args, **kwargs):
        """
        Initialise le formulaire avec l'uid et le token de l'URL
        """
        super().__init__(*args, **kwargs)
        self.uid = uid
        self.token = token
        self.user = None

    def clean_new_password(self):
        """
        Validation du mot de passe :
        - minimum 8 caractères
        - au moins une majuscule
        - au moins une minuscule
        - au moins un chiffre
        """
        password = self.cleaned_data.get('new_password')

        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")

        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")

        if not re.search(r'\d', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")

        return password

    def clean(self):
        """
        Vérifie que :
        1. Les deux mots de passe correspondent
        2. Le token est valide
        3. L'utilisateur existe
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        password_confirm = cleaned_data.get('new_password_confirm')

        # Vérifier que les mots de passe correspondent
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        # Décoder l'UID et récupérer l'utilisateur
        try:
            uid = force_str(urlsafe_base64_decode(self.uid))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise forms.ValidationError("Lien de réinitialisation invalide.")

        # Vérifier la validité du token
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(self.user, self.token):
            raise forms.ValidationError(
                "Le lien de réinitialisation est expiré ou invalide. "
                "Veuillez demander un nouveau lien de réinitialisation."
            )

        return cleaned_data

    def save(self):
        """
        Change le mot de passe de l'utilisateur
        """
        if self.user:
            self.user.set_password(self.cleaned_data['new_password'])
            self.user.save()
            return self.user
        return None
