from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products_list, name='products-list'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),
    path('products/<int:pk>/similar/', views.product_similar, name='product-similar'),
]
