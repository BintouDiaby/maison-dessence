from django.urls import path
from .views import InteractionCreateView, InteractionListView

urlpatterns = [
    path('interactions/', InteractionListView.as_view(), name='interactions-list'),
    path('interactions/create/', InteractionCreateView.as_view(), name='interactions-create'),
]
