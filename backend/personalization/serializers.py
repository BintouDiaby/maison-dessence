from rest_framework import serializers
from .models import Conversation, ConversationMessage


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = ('id', 'role', 'text', 'created_at')
        read_only_fields = ('id', 'created_at')


class ConversationSerializer(serializers.ModelSerializer):
    messages = ConversationMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'user', 'created_at', 'status', 'metadata', 'suggested_recipe', 'messages')
        read_only_fields = ('id', 'created_at', 'user', 'suggested_recipe')
