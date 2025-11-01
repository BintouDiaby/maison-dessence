"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.http import Http404
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),
    path('api/', include('users.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('interactions.urls')),
    path('api/', include('recommendations.urls')),
    path('api/', include('personalization.urls')),
    # No static frontend served by Django by default. If you want to serve
    # a static index, add a TemplateView here and set TEMPLATES['DIRS'].
    # Serve the static frontend index (from frontend/static_site/index.html)
    path('', TemplateView.as_view(template_name='index.html')),
    # Development helper: render any *.html file placed in the templates dirs
    # so pages like /login.html, /products.html, /product.html work without
    # a dedicated view. In production prefer serving a built frontend or
    # use proper template views.
    re_path(r'^(?P<path>.*\.html)$', lambda request, path: (_render_html(request, path))),
]


def _render_html(request, path):
    try:
        return render(request, path)
    except TemplateDoesNotExist:
        raise Http404()


# Serve media files uploaded during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
