from django.urls import path
from .views import (
    CreateConversationView,
    MessageCreateView,
    ConversationDetailView,
    ConversationListView,
    FinalizeConversationView,
)

urlpatterns = [
    path('conversations/create/', CreateConversationView.as_view(), name='personalize-create-conversation'),
    path('conversations/', ConversationListView.as_view(), name='personalize-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='personalize-detail'),
    path('conversations/<int:conv_id>/messages/', MessageCreateView.as_view(), name='personalize-messages'),
    path('conversations/<int:conv_id>/finalize/', FinalizeConversationView.as_view(), name='personalize-finalize'),
]
