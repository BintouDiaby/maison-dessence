# backend/core/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.http import Http404
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # APIs
    path('api/', include('products.urls')),
    path('api/', include('users.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('interactions.urls')),
    path('api/', include('recommendations.urls')),
    path('api/', include('personalization.urls')),

    # Front statique (templates *.html)
    path('', TemplateView.as_view(template_name='index.html')),
    re_path(r'^(?P<path>.*\.html)$', lambda request, path: (_render_html(request, path))),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

def _render_html(request, path):
    try:
        return render(request, path)
    except TemplateDoesNotExist:
        raise Http404()

# Media en dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
