from rest_framework import viewsets

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


class ComicBookViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ComicBook.objects.all()
    serializer_class = ComicBookListSerializer
    detail_serializer_class = ComicBookDetailSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return ComicBook.objects.prefetch_related('comicbookauthor_set')
        return ComicBook.objects.all()
