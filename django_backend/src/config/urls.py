from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from qazline import urls as qazline_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(qazline_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
