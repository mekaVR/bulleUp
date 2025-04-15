from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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
    path('register/', UserRegister.as_view(), name='user-register'),
    path('api/', include(router.urls))
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)