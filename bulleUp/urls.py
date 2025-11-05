from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import *
from bdtheque.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'comic-book', ComicBookViewSet, basename='comic-book')
router.register(r'author', AuthorsViewSet, basename='author')
router.register(r'publisher', PublisherViewSet, basename='publisher')
router.register(r'review', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegister.as_view(), name='user-register'),
    path('register/get-user-exist/', UserRegister.get_user_exist, name='get-user-exist'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('reset-password/<str:uid>/<str:token>/', PasswordResetFormView.as_view(), name='password-reset-form'),
    path('api/', include(router.urls))
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)