from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from authentication.models import User
from .serializers import *

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

    def get_queryset(self):
        if self.action == 'retrieve':
            return User.objects.prefetch_related(
                'review_set', 'usercollection_set', 'userwishlist_set', 'follows'
            )
        return User.objects.all()


    @action(detail=True, methods=['post'])
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


    @action(detail=True, methods=['post'])
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


class ComicBookViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ComicBookListSerializer
    detail_serializer_class = ComicBookDetailSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return ComicBook.objects.prefetch_related('comicbookauthor_set')
        return ComicBook.objects.all()

    @action(detail=True, methods=['post'])
    def add_comic_in_collection(self, request, pk=None):
        try:
            comic_to_add = ComicBook.objects.get(pk=pk)
            request.user.add_comic_in_collection(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez ajouter {comic_to_add.title} à votre collection"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_comic_in_collection(self, request, pk=None):
        try:
            comic_to_remove = ComicBook.objects.get(pk=pk)
            request.user.remove_comic_in_collection(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez enlever {comic_to_remove.title} de votre collection"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_comic_in_wishlist(self, request, pk=None):
        try:
            comic_to_add = ComicBook.objects.get(pk=pk)
            request.user.add_comic_in_wishlist(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez ajouter {comic_to_add.title} à votre wishlist"},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_comic_in_wishlist(self, request, pk=None):
        try:
            comic_to_remove = ComicBook.objects.get(pk=pk)
            request.user.remove_comic_in_wishlist(pk)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": f"Vous avez enlever {comic_to_remove.title} de votre wishlist"},
                        status=status.HTTP_200_OK)


class AuthorsViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = AuthorListSerializer
    detail_serializer_class = AuthorDetailSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return Author.objects.prefetch_related('comicbookauthor_set')
        return Author.objects.all()
