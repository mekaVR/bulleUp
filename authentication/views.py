from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import *

from authentication.serializers import UserRegisterSerializer

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