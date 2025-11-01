from rest_framework import generics, permissions
from .models import Interaction
from .serializers import InteractionSerializer


class InteractionCreateView(generics.CreateAPIView):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        interaction = serializer.save(user=self.request.user)
        # append to user's profile history if available
        try:
            profile = self.request.user.profile
            hist = profile.history or []
            hist_entry = {
                'event_type': interaction.event_type,
                'product_id': interaction.product_id,
                'value': interaction.value,
                'metadata': interaction.metadata,
                'created_at': interaction.created_at.isoformat(),
            }
            hist.append(hist_entry)
            profile.history = hist
            profile.save()
        except Exception:
            # try creating profile if missing, then append
            try:
                profile = getattr(self.request.user, 'profile', None)
                if profile is None:
                    from users.models import Profile
                    profile = Profile.objects.create(user=self.request.user)
                hist = profile.history or []
                hist_entry = {
                    'event_type': interaction.event_type,
                    'product_id': interaction.product_id,
                    'value': interaction.value,
                    'metadata': interaction.metadata,
                    'created_at': interaction.created_at.isoformat(),
                }
                hist.append(hist_entry)
                profile.history = hist
                profile.save()
            except Exception:
                pass


class InteractionListView(generics.ListAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return interactions for the authenticated user
        user = self.request.user
        return Interaction.objects.filter(user=user).order_by('-created_at')
from django.shortcuts import render

# Create your views here.
