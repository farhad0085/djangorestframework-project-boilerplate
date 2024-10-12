from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path('paypal/', include('paypal.standard.ipn.urls')),
    # path('payment/', include('payment.urls'), name="payment"),
    path('api/events/', include('event.urls')),
    path('api/auth/', include('user.urls')),
]
if settings.DEBUG:
    # media urls
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
