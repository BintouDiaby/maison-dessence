from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
import json
import re
import time
from datetime import date
from django.core.cache import cache
import logging

from .models import Conversation, ConversationMessage
from .serializers import ConversationSerializer, ConversationMessageSerializer

logger = logging.getLogger(__name__)

from django.core.mail import send_mail

# try to import openai if available; if not, we'll fall back to the internal mock
try:
    import openai
    if getattr(settings, 'OPENAI_API_KEY', ''):
        openai.api_key = settings.OPENAI_API_KEY
    else:
        # don't set an API key if not present
        openai = None
except Exception:
    openai = None


class CreateConversationView(generics.CreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a conversation. Owners can access their conversations; staff users
    (admins) can access any conversation.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Conversation.objects.all()

    def get_object(self):
        obj = super().get_object()
        # allow owner or staff
        user = self.request.user
        if obj.user_id != user.id and not (user and user.is_staff):
            raise permissions.PermissionDenied()
        return obj


class ConversationListView(generics.ListAPIView):
    """
    List conversations for the requesting user. Admins (staff) see all conversations.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_staff:
            return Conversation.objects.all().order_by('-created_at')
        return Conversation.objects.filter(user=user).order_by('-created_at')


def _mock_assistant_reply_for(text):
    # Very small heuristic-based mock that returns an assistant text and optionally a recipe
    text_low = (text or '').lower()
    reply = "Merci — peux‑tu préciser tes notes préférées (ex: floral, vanille, boisé), l'intensité et le budget ?"
    recipe = None
    # if user seems to ask for a full perfume, return a sample recipe
    triggers = ['crée', 'créer', 'formule', 'final', 'personnalise', 'compose', 'compose-moi', 'je veux un']
    if any(t in text_low for t in triggers) or 'recette' in text_low:
        reply = "Voici une proposition de formule personnalisée basée sur vos goûts — vous pouvez la finaliser ou demander des ajustements."
        recipe = {
            'name': 'Signature Personnalisée',
            'top_notes': ['bergamot', 'lemon'],
            'heart_notes': ['rose', 'jasmine'],
            'base_notes': ['vanilla', 'amber'],
            'proportions': {'bergamot': 8, 'lemon': 7, 'rose': 25, 'jasmine': 20, 'vanilla': 25, 'amber': 15},
            'comments': 'A floral oriental for an elegant everyday wear.'
        }
    return reply, recipe


class MessageCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conv_id=None):
        # conv_id optional: if not present, require conversation id in body
        conv = None
        if conv_id:
            conv = get_object_or_404(Conversation, pk=conv_id)
            if conv.user_id != request.user.id:
                return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        else:
            cid = request.data.get('conversation')
            if not cid:
                return Response({'detail': 'conversation id required'}, status=status.HTTP_400_BAD_REQUEST)
            conv = get_object_or_404(Conversation, pk=cid)
            if conv.user_id != request.user.id:
                return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        role = request.data.get('role', 'user')
        text = request.data.get('text', '')
        if not text:
            return Response({'detail': 'text required'}, status=status.HTTP_400_BAD_REQUEST)

        msg = ConversationMessage.objects.create(conversation=conv, role=role, text=text)

        response_payload = {'message': ConversationMessageSerializer(msg).data}

        # Only auto-generate assistant reply when the user sends a message
        if role == 'user':
            assistant_text = None
            recipe = None

            # If OpenAI is configured and import succeeded, try to call it
            if openai is not None:
                # simple throttling / quota protection per user (dev-friendly)
                user = request.user
                if user and user.is_authenticated:
                    # minimum interval between requests in seconds
                    min_interval = getattr(settings, 'OPENAI_MIN_INTERVAL_SECS', 10)
                    daily_limit = getattr(settings, 'OPENAI_DAILY_LIMIT', 200)
                    last_key = f'openai_last_{user.id}'
                    count_key = f'openai_count_{user.id}_{date.today().isoformat()}'
                    last_ts = cache.get(last_key)
                    if last_ts and (time.time() - float(last_ts) < min_interval):
                        retry_after = int(min_interval - (time.time() - float(last_ts)))
                        return Response({'detail': 'rate_limited', 'retry_after': retry_after}, status=429)
                    count = cache.get(count_key, 0)
                    if count >= daily_limit:
                        return Response({'detail': 'daily_quota_exceeded'}, status=429)
                try:
                    started = time.time()
                    system_prompt = (
                        "Tu es un assistant expert en parfumerie. "
                        "Aide l'utilisateur à composer une formule de parfum personnalisée. "
                        "Si l'utilisateur demande explicitement une formule, retourne une réponse naturelle en français. "
                        "Si possible, inclus une section JSON délimitée par des accolades contenant les clés: name, top_notes, heart_notes, base_notes, proportions, comments."
                    )
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ]
                    resp = openai.ChatCompletion.create(
                        model=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7,
                    )
                    assistant_text = resp.choices[0].message.get('content', '').strip()

                    # metrics & logging: time taken and usage if present
                    elapsed = time.time() - started
                    usage = resp.get('usage') if isinstance(resp, dict) else getattr(resp, 'usage', None)
                    try:
                        # increment a simple cache-based counter for total calls
                        cache_key_calls = 'metrics_openai_calls_total'
                        prev_calls = int(cache.get(cache_key_calls, 0) or 0)
                        cache.set(cache_key_calls, prev_calls + 1, timeout=None)
                        if usage and isinstance(usage, dict):
                            # some SDKs return usage.total_tokens or usage.token counts
                            total_tokens = usage.get('total_tokens') or usage.get('completion_tokens') or usage.get('prompt_tokens')
                            cache_key_tokens = 'metrics_openai_tokens_total'
                            prev_t = int(cache.get(cache_key_tokens, 0) or 0)
                            try:
                                prev_t = int(prev_t)
                            except Exception:
                                prev_t = 0
                            if total_tokens:
                                try:
                                    cache.set(cache_key_tokens, prev_t + int(total_tokens), timeout=None)
                                except Exception:
                                    pass
                    except Exception:
                        pass

                    logger.info('OpenAI call succeeded', extra={'user_id': getattr(user, 'id', None), 'elapsed_s': elapsed, 'usage': usage})

                    # update throttling counters after successful call
                    if user and user.is_authenticated:
                        cache.set(last_key, str(time.time()), timeout=3600)
                        # increment daily counter safely
                        prev = cache.get(count_key, 0)
                        try:
                            prev = int(prev)
                        except Exception:
                            prev = 0
                        cache.set(count_key, prev + 1, timeout=60 * 60 * 48)

                    # try to find a JSON object in the assistant text
                    m = re.search(r"(\{[\s\S]*\})", assistant_text)
                    if m:
                        try:
                            candidate = m.group(1)
                            parsed = json.loads(candidate)
                            # basic validation of expected keys
                            if isinstance(parsed, dict) and 'name' in parsed:
                                recipe = parsed
                        except Exception:
                            # ignore JSON parse errors and fall back to no recipe
                            recipe = None
                except Exception as e:
                    # if the OpenAI call fails for any reason, fall back to mock
                    assistant_text = None

            # if openai wasn't used or didn't produce a reply, use the mock
            if not assistant_text:
                assistant_text, recipe = _mock_assistant_reply_for(text)

            assistant_msg = ConversationMessage.objects.create(conversation=conv, role='assistant', text=assistant_text)
            response_payload['assistant'] = ConversationMessageSerializer(assistant_msg).data
            if recipe:
                conv.suggested_recipe = recipe
                conv.save()
                response_payload['suggested_recipe'] = recipe

        return Response(response_payload, status=status.HTTP_201_CREATED)


class FinalizeConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conv_id):
        conv = get_object_or_404(Conversation, pk=conv_id)
        if conv.user_id != request.user.id:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        # Do not allow finalizing a conversation that has no suggested recipe
        if not conv.suggested_recipe:
            return Response({'detail': 'No suggested recipe to finalize. Ask the assistant for a recipe first.'}, status=status.HTTP_400_BAD_REQUEST)

        conv.status = 'finalized'
        conv.save()

        # Try to send the suggested recipe to the user via email if email backend configured
        try:
            user_email = getattr(conv.user, 'email', None)
            if user_email:
                subject = 'Votre formule personnalisée — Maison d\'essence'
                body = 'Bonjour %s,\n\nVoici la formule personnalisée que nous avons préparée pour vous :\n\n%s\n\nCordialement,\nMaison d\'essence' % (
                    getattr(conv.user, 'first_name', conv.user.username or ''), json.dumps(conv.suggested_recipe, indent=2, ensure_ascii=False)
                )
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
                # send_mail will use the configured EMAIL_BACKEND (console or SMTP)
                send_mail(subject, body, from_email, [user_email], fail_silently=True)
        except Exception as e:
            logger.exception('Failed to send finalized recipe email for conversation %s', conv.id)

        return Response({'status': 'finalized', 'conversation': conv.id})
