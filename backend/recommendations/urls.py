from django.urls import path
from .views import TrainRecommenderView, SimilarProductsView, DemoView

urlpatterns = [
    path('recommender/train/', TrainRecommenderView.as_view(), name='recommender-train'),
    path('recommender/products/<int:product_id>/', SimilarProductsView.as_view(), name='recommender-similar'),
    path('recommender/demo/', DemoView.as_view(), name='recommender-demo'),
]
