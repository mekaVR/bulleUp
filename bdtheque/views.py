from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import logging

from authentication.models import User
from .models import *
from .serializers import *

logger = logging.getLogger(__name__)

class MultipleSerializerMixin:
    detail_serializer_class = None
    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class UsersViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    detail_serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'retrieve':
            return User.objects.prefetch_related(
                'review_set', 'usercollection_set', 'userwishlist_set', 'follows', 'authorfollow_set', 'publisherfollow_set'
            )
        return User.objects.all()


    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        if request.method == 'GET':
            user = User.objects.prefetch_related(
                'usercollection_set',
                'userwishlist_set',
                'review_set',
                'loans',
                'follows',
                'authorfollow_set',
                'publisherfollow_set'
            ).get(pk=request.user.pk)

            serializer = UserProfileSerializer(user, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = UserProfileUpdateSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid():
                serializer.save()

                updated_user = User.objects.prefetch_related(
                    'usercollection_set',
                    'userwishlist_set',
                    'review_set',
                    'loans',
                    'follows',
                    'authorfollow_set',
                    'publisherfollow_set'
                ).get(pk=request.user.pk)

                response_serializer = UserProfileSerializer(updated_user, context={'request': request})

                return Response(
                    {
                        "message": "Profil mis à jour avec succès",
                        "user": response_serializer.data
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {
                    "error": "Données invalides",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return None

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='change-password'
    )
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            return Response(
                {"error": "Tous les champs sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(old_password, user.password):
            return Response(
                {"error": "L'ancien mot de passe est incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response(
                {"error": "Les nouveaux mots de passe ne correspondent pas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {"error": "Mot de passe invalide", "details": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        try:
            send_mail(
                subject='Mot de passe modifié - BulleUp',
                message=f"""
                    Bonjour {user.username},
                    
                    Votre mot de passe a été modifié avec succès.
                    
                    Si vous n'êtes pas à l'origine de cette modification, veuillez contacter immédiatement notre support.
                    
                    Cordialement,
                    L'équipe BulleUp
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")

        return Response(
            {"message": "Mot de passe modifié avec succès. Un email de confirmation a été envoyé."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_follower(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({"error": "Vous devez être connecté pour suivre un utilisateur"},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_to_follow = User.objects.get(pk=pk)
            request.user.add_follower(user_to_follow)
        except User.DoesNotExist:
            return Response({"error": "L'utilisateur que vous essayez de suivre n'existe pas"},
                            status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"Vous suivez maintenant {user_to_follow.username}"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_follower(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({"error": "Vous devez être connecté pour suivre un utilisateur"},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_to_remove = User.objects.get(pk=pk)
            request.user.remove_follower(user_to_remove)
        except User.DoesNotExist:
            return Response({"error": "L'utilisateur n'existe pas"},
                            status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"Vous ne suivez plus {user_to_remove.username}"},
                        status=status.HTTP_200_OK)

    # =========================================================================
    # ENDPOINT SUPPRESSION DE COMPTE : DELETE /api/users/delete-account/
    # =========================================================================

    @action(
        detail=False,
        methods=['delete'],
        permission_classes=[IsAuthenticated],
        url_path='delete-account'
    )
    def delete_account(self, request):
        """
        Permet à l'utilisateur de supprimer son propre compte.

        ENDPOINT : DELETE /api/users/delete-account/

        BODY :
        {
            "password": "mot_de_passe_actuel"
        }

        SÉCURITÉ :
        ---------
        1. Authentification JWT requise
        2. Confirmation du mot de passe obligatoire
        3. Email de notification envoyé
        4. Suppression en cascade automatique :
           - Collection de BDs
           - Wishlist
           - Reviews
           - Prêts
           - Follows
           - Avatar (via django-cleanup)

        CONCEPTS REST :
        ------------
        - DELETE : Suppression d'une ressource
        - 200 OK : Suppression réussie
        - 400 Bad Request : Mot de passe manquant
        - 401 Unauthorized : Mot de passe incorrect

        EXEMPLES :
        ---------
        DELETE /api/users/delete-account/
        Headers: Authorization: Bearer <token>
        Body: {"password": "mon_mot_de_passe"}

        IMPORTANT :
        ----------
        Cette action est IRRÉVERSIBLE. Toutes les données de l'utilisateur
        seront définitivement supprimées.
        """
        user = request.user
        password = request.data.get('password')

        # Validation 1 : Le mot de passe est requis
        if not password:
            return Response(
                {"error": "Le mot de passe est requis pour confirmer la suppression"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation 2 : Vérifier que le mot de passe est correct
        if not check_password(password, user.password):
            return Response(
                {"error": "Mot de passe incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Sauvegarder les infos pour l'email (avant suppression)
        username = user.username
        email = user.email
        user_id = user.id

        # Envoyer un email de confirmation
        try:
            send_mail(
                subject='Compte supprimé - BulleUp',
                message=f"""
Bonjour {username},

Votre compte BulleUp a été supprimé avec succès.

Toutes vos données ont été effacées :
- Collection de bandes dessinées
- Liste de souhaits
- Avis et critiques
- Prêts en cours
- Abonnements

Si vous n'êtes pas à l'origine de cette suppression, contactez immédiatement notre support à support@bulleup.com.

Nous espérons vous revoir bientôt !

Cordialement,
L'équipe BulleUp
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,  # Ne pas bloquer si l'email échoue
            )
        except Exception as e:
            # Logger l'erreur mais ne pas empêcher la suppression
            logger.error(f"Erreur lors de l'envoi de l'email de suppression de compte : {e}")

        # Log pour traçabilité (avant suppression)
        logger.warning(
            f"SUPPRESSION DE COMPTE : {username} (ID: {user_id}, Email: {email})"
        )

        # Supprimer l'utilisateur
        # Django supprime automatiquement toutes les données liées (CASCADE)
        # django-cleanup supprime automatiquement l'avatar
        user.delete()

        return Response(
            {
                "message": "Votre compte a été supprimé avec succès. Nous espérons vous revoir bientôt !"
            },
            status=status.HTTP_200_OK
        )


class ComicBookViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ComicBookListSerializer
    detail_serializer_class = ComicBookDetailSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return ComicBook.objects.prefetch_related('comicbookauthor_set')
        return ComicBook.objects.all()

    @action(detail=False, methods=['get'], url_path='by-ean/(?P<ean>[^/.]+)')
    def get_by_ean(self, request, ean=None):
        comic_book = get_object_or_404(ComicBook, ean=ean)
        serializer = self.get_serializer(comic_book)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_comic_in_collection(self, request, pk=None):
        try:
            comic_to_add = ComicBook.objects.get(pk=pk)
            request.user.add_comic_in_collection(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez ajouter {comic_to_add.title} à votre collection"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_comic_in_collection(self, request, pk=None):
        try:
            comic_to_remove = ComicBook.objects.get(pk=pk)
            request.user.remove_comic_in_collection(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez enlever {comic_to_remove.title} de votre collection"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_comic_in_wishlist(self, request, pk=None):
        try:
            comic_to_add = ComicBook.objects.get(pk=pk)
            request.user.add_comic_in_wishlist(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez ajouter {comic_to_add.title} à votre wishlist"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_comic_in_wishlist(self, request, pk=None):
        try:
            comic_to_remove = ComicBook.objects.get(pk=pk)
            request.user.remove_comic_in_wishlist(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez enlever {comic_to_remove.title} de votre wishlist"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def loan_comic_book(self, request, pk=None):
        username = request.data.get('username')
        user_id = request.data.get('user_id')

        try:
            friend = None
            kwargs = {
                "comic_book": ComicBook.objects.get(pk=pk),
                "user": request.user
            }
            comic_book = ComicBook.objects.get(pk=pk)
            if user_id:
                kwargs['friend'] = User.objects.get(pk=user_id)
                friend = kwargs['friend'].username
            else:
                friend = username
                kwargs['username'] = username
            request.user.loan_comic_book(kwargs)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez preté votre bd {comic_book.title} à {friend}"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def return_loan(self, request, pk=None):
        try:
            loan_id = request.data.get('loan_id')
            if not loan_id:
                return Response({"error": "loan_id est requis"},
                              status=status.HTTP_400_BAD_REQUEST)
            loan = Loan.objects.get(pk=loan_id, user=request.user)
            comic_book = loan.comic_book
            loan.delete()

            return Response({"message": f"Vous avez récupéré {comic_book.title}"},
                          status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response({"error": "Prêt non trouvé ou vous n'êtes pas propriétaire de ce prêt"},
                          status=status.HTTP_404_NOT_FOUND)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class AuthorsViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AuthorListSerializer
    detail_serializer_class = AuthorDetailSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return Author.objects.prefetch_related('comicbookauthor_set')
        return Author.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow_author(self, request, pk=None):
        author = Author.objects.get(pk=pk)
        try:
            request.user.follow_author(pk)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous suivez {author.first_name} {author.last_name}"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow_author(self, request, pk=None):
        author = Author.objects.get(pk=pk)
        try:
            request.user.unfollow_author(pk)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez arrêté de suivre {author.first_name} {author.last_name}"},
                        status=status.HTTP_200_OK)


class PublisherViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherMiniSerializer
    detail_serializer_class = PublisherSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow_publisher(self, request, pk=None):
        publisher = Publisher.objects.get(pk=pk)
        try:
            request.user.follow_publisher(pk)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous suivez {publisher.name}"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow_publisher(self, request, pk=None):
        publisher = Publisher.objects.get(pk=pk)
        try:
            request.user.unfollow_publisher(pk)
        except ValueError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez arrêté de suivre {publisher.name}"},
                        status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer