from rest_framework import serializers
from .models import Interaction


class InteractionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Interaction
        fields = ('id', 'user', 'product_id', 'event_type', 'value', 'metadata', 'created_at')
        read_only_fields = ('id', 'created_at', 'user')

    def validate_event_type(self, value):
        allowed = [c[0] for c in Interaction.EVENT_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError('Invalid event_type')
        return value
