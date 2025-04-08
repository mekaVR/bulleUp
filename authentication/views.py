from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import *

from authentication.serializers import UserRegisterSerializer

class UserRegister(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)