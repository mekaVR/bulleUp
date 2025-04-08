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