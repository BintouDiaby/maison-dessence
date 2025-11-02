# backend/products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('products/', views.products_list, name='products-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    path('products/<int:pk>/similar/', views.product_similar, name='product-similar'),

    # CRUD vendeur (pas de 'api/' ici)
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Upload fichier image
    path('products/<int:pk>/upload-image/', views.product_upload_image, name='product_upload_image'),
]
