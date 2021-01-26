from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# from rest_framework_social_oauth2 import urls as oauth2_urls

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

from qazline import urls as qazline_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(qazline_urls)),
    # path('auth/', include(oauth2_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
