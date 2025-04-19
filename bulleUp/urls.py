from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authentication.views import *
from bdtheque.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'comic-book', ComicBookViewSet, basename='comic-book')
router.register(r'author', AuthorsViewSet, basename='author')
router.register(r'review', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegister.as_view(), name='user-register'),
    path('api/', include(router.urls))
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)