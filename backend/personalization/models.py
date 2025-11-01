from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('finalized', 'Finalized')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='open')
    metadata = models.JSONField(default=dict, blank=True)
    suggested_recipe = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Conversation {self.id} user={self.user_id} status={self.status}"


class ConversationMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')]
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Msg {self.role} conv={self.conversation_id} at={self.created_at.isoformat()}"
