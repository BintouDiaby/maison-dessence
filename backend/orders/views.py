from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework import status


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # only authenticated users can create orders
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Attach the authenticated user
        serializer.save(user=self.request.user)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return the orders of the authenticated user
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only retrieve their own orders
        user = self.request.user
        return Order.objects.filter(user=user)
from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from .models import Cart, CartItem
from .serializers import CartSerializer, AddCartItemSerializer, CheckoutSerializer, PaymentSerializer
from products.models import Product
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
import stripe
import json
import time
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import requests

logger = logging.getLogger(__name__)


def _get_or_create_cart(user):
    if not user.is_authenticated:
        return None
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart = _get_or_create_cart(request.user)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)


class AddCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = Product.objects.get(id=product_id)
        cart = _get_or_create_cart(request.user)

        ci, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id, defaults={'quantity': quantity, 'unit_price': product.price})
        if not created:
            ci.quantity += quantity
            ci.unit_price = product.price
            ci.save()

        return Response({'ok': True, 'cart': CartSerializer(cart).data})


class RemoveCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)
        cart = _get_or_create_cart(request.user)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response({'ok': True, 'cart': CartSerializer(cart).data})


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_method = serializer.validated_data['payment_method']

        cart = _get_or_create_cart(request.user)
        items = []
        for ci in cart.items.all():
            items.append({'product_id': ci.product_id, 'quantity': ci.quantity, 'price': str(ci.unit_price)})

        total = cart.total()

        # For now we implement a mocked payment flow. If you later want Stripe, we can add it.
        if payment_method in ('mock', 'card'):
            # simulate payment success
            transaction_id = f"MOCK-{int(timezone.now().timestamp())}"
            order = Order.objects.create(user=request.user, items=items, total=total, status='paid')
            # clear cart
            cart.items.all().delete()
            return Response({'ok': True, 'order_id': order.id, 'transaction_id': transaction_id})

        return Response({'detail': 'unsupported payment method'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentMockView(APIView):
    """Accepts basic payment data and returns a simulated result. DO NOT use in production."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        # very simple simulation: accept if method==mock or card number provided
        if data.get('method') == 'mock' or (data.get('card') and data['card'].get('number')):
            tx = f"MOCKPAY-{int(timezone.now().timestamp())}"
            return Response({'ok': True, 'transaction_id': tx})
        return Response({'ok': False}, status=status.HTTP_400_BAD_REQUEST)


class CreateStripePaymentIntentView(APIView):
    """Create a Stripe PaymentIntent for the current cart and return client_secret.
    Expects authenticated user. Creates an Order with status 'pending' and attaches metadata.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # require stripe key
        if not settings.STRIPE_SECRET_KEY:
            return Response({'detail': 'Stripe not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        cart = _get_or_create_cart(request.user)
        if not cart or cart.items.count() == 0:
            return Response({'detail': 'cart empty'}, status=status.HTTP_400_BAD_REQUEST)

        items = []
        for ci in cart.items.all():
            items.append({'product_id': ci.product_id, 'quantity': ci.quantity, 'price': str(ci.unit_price)})

        total_decimal = cart.total()
        # Stripe expects amount in cents
        try:
            amount_cents = int(total_decimal * 100)
        except Exception:
            # fallback
            amount_cents = int(float(str(total_decimal)) * 100)

        # create order in pending status
        order = Order.objects.create(user=request.user, items=items, total=total_decimal, status='pending')

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='eur',
                metadata={'order_id': str(order.id)},
                description=f'Maison d\'essence order #{order.id}',
            )
        except Exception as e:
            logger.exception('Stripe PaymentIntent creation failed')
            return Response({'detail': 'payment_intent_failed', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'client_secret': intent.client_secret, 'order_id': order.id})


class CreateCinetpayPaymentView(APIView):
    """Create a CinetPay payment and return the payment URL to redirect the user to.

    This implementation calls CinetPay's checkout API. Configure the following env vars in
    `backend/core/settings.py` or environment:
      - CINETPAY_SITE_ID
      - CINETPAY_API_KEY
      - CINETPAY_BASE_URL (optional, defaults to CinetPay sandbox endpoint)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Read cart and buyer info
        cart_items = request.data.get('items') or []
        buyer = request.data.get('buyer', {})

        # compute total from items if possible, fallback to provided total
        try:
            total = sum((float(i.get('price', 0)) * int(i.get('qty', 1))) for i in cart_items)
        except Exception:
            total = 0

        if total <= 0:
            return Response({'detail': 'cart empty or invalid'}, status=status.HTTP_400_BAD_REQUEST)
        # create order record (so we can return a mock confirm URL if CinetPay isn't configured)
        items = []
        for it in cart_items:
            items.append({'product_id': it.get('id'), 'quantity': it.get('qty'), 'price': str(it.get('price'))})

        order = Order.objects.create(user=request.user if request.user and request.user.is_authenticated else None,
                                     items=items, total=total, status='pending')

        # Ensure config
        site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
        api_key = getattr(settings, 'CINETPAY_API_KEY', '')
        base_url = getattr(settings, 'CINETPAY_BASE_URL', 'https://sandbox.cinetpay.com/v2/payment')

        if not site_id or not api_key:
            # If CinetPay isn't configured in this environment return a local mock URL
            mock_url = request.build_absolute_uri(f'/api/orders/cinetpay/confirm/?order_id={order.id}&status=success')
            return Response({'payment_url': mock_url, 'order_id': order.id})

        # Prepare payload for CinetPay
        transaction_id = f"CINETPAY-{order.id}-{int(time.time())}"
        payload = {
            'amount': int(total),
            'currency': 'XOF' if getattr(settings, 'CURRENCY', 'EUR') == 'XOF' else 'EUR',
            'site_id': site_id,
            'transaction_id': transaction_id,
            'description': f"Maison d'Essence order #{order.id}",
            'return_url': request.build_absolute_uri(f"/orders/{order.id}/confirmation/"),
            'notify_url': request.build_absolute_uri('/api/orders/cinetpay/webhook/'),
            'customer_name': buyer.get('name') or '',
            'customer_email': buyer.get('email') or '',
        }

        try:
            # CinetPay's API expects a POST; adapt to their exact contract in production
            resp = requests.post(base_url, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            # assume API returns payment_url in data['data']['payment_url'] or similar
            payment_url = data.get('data', {}).get('payment_url') or data.get('payment_url')
            if not payment_url:
                return Response({'detail': 'cinetpay_error', 'raw': data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'payment_url': payment_url, 'order_id': order.id})

        except requests.RequestException as e:
            logger.exception('CinetPay request failed')
            return Response({'detail': 'cinetpay_request_failed', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Backwards-compatible class names used by URLs elsewhere in the project
class CreateCinetPayTransactionView(CreateCinetpayPaymentView):
    pass


class CinetPayConfirmView(APIView):
    """Simple confirmation endpoint that CinetPay can redirect to after payment.

    This view is minimal for development: it accepts GET params or POST JSON containing
    an `order_id` (or transaction_id) and marks the order paid. In production use the
    official webhook verification flow.
    """
    permission_classes = []

    def get(self, request):
        order_id = request.GET.get('order_id') or request.GET.get('transaction_id')
        if not order_id:
            return Response({'detail': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(id=int(order_id))
            order.status = 'paid'
            order.save()
            return Response({'detail': 'order marked paid'})
        except Exception:
            return Response({'detail': 'order not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        return self.get(request)


class StripeConfigView(APIView):
    """Return Stripe publishable key for client-side initialization."""
    permission_classes = []

    def get(self, request):
        # It's fine to expose the publishable key to the client-side.
        return Response({'publishableKey': settings.STRIPE_PUBLISHABLE_KEY})


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Endpoint to receive Stripe webhooks (in test mode)."""
    permission_classes = []  # allow anonymous webhook posts

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        if not settings.STRIPE_WEBHOOK_SECRET:
            # fallback: try to parse without verification (only in dev)
            try:
                event = json.loads(payload)
            except Exception as e:
                logger.exception('Invalid payload')
                return HttpResponse(status=400)
        else:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
            except Exception as e:
                logger.exception('Webhook signature verification failed')
                return HttpResponse(status=400)

        # Handle the event
        typ = event.get('type')
        data = event.get('data', {}).get('object', {})

        if typ == 'payment_intent.succeeded':
            metadata = data.get('metadata', {})
            order_id = metadata.get('order_id')
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = 'paid'
                    order.save()
                    # clear cart for user if present
                    if order.user and hasattr(order.user, 'cart'):
                        order.user.cart.items.all().delete()
                except Order.DoesNotExist:
                    logger.warning('Order not found for webhook order_id=%s', order_id)

        # return 200
        return HttpResponse(status=200)


class CreateCinetPayTransactionView(APIView):
    """Create a CinetPay transaction or return a mock URL for dev if not configured."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = _get_or_create_cart(request.user)
        if not cart or cart.items.count() == 0:
            return Response({'detail': 'cart empty'}, status=status.HTTP_400_BAD_REQUEST)

        total_decimal = cart.total()
        # create order pending
        order = Order.objects.create(user=request.user, items=[{'product_id': ci.product_id, 'quantity': ci.quantity, 'price': str(ci.unit_price)} for ci in cart.items.all()], total=total_decimal, status='pending')

        # If CinetPay not configured, return a mock payment URL which simulates the redirect
        from django.conf import settings
        api_key = getattr(settings, 'CINETPAY_API_KEY', '')
        site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
        if not api_key or not site_id:
            # create a local mock confirmation URL
            mock_url = request.build_absolute_uri(f'/api/orders/cinetpay/confirm/?order_id={order.id}&status=success')
            return Response({'payment_url': mock_url, 'order_id': order.id})

        # Real CinetPay integration would go here. For safety we implement a minimal initializer.
        try:
            import requests
            payload = {
                'amount': str(int(total_decimal * 100)),
                'currency': 'XOF',
                'site_id': site_id,
                'apikey': api_key,
                'transaction_id': str(order.id),
                'return_url': request.build_absolute_uri(f'/api/orders/cinetpay/confirm/?order_id={order.id}'),
                'notify_url': request.build_absolute_uri(f'/api/orders/cinetpay/confirm/')
            }
            # NOTE: endpoint URL and parameters may differ; adapt with real CinetPay docs and credentials.
            resp = requests.post('https://api.cinetpay.com/v1/?/transaction/init', json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            payment_url = data.get('payment_url') or data.get('data', {}).get('payment_url')
            if not payment_url:
                return Response({'detail': 'cinetpay init failed', 'raw': data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'payment_url': payment_url, 'order_id': order.id})
        except Exception as e:
            logger.exception('CinetPay init failed')
            return Response({'detail': 'cinetpay_error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CinetPayConfirmView(APIView):
    """Simple endpoint to handle CinetPay return/notify and mark order as paid (dev-friendly)."""
    permission_classes = []

    def get(self, request):
        order_id = request.GET.get('order_id')
        status_q = request.GET.get('status', 'success')
        if not order_id:
            return HttpResponse('missing order_id', status=400)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse('order not found', status=404)
        if status_q == 'success':
            order.status = 'paid'
            order.save()
            # clear cart
            if order.user and hasattr(order.user, 'cart'):
                order.user.cart.items.all().delete()
            # redirect to a simple thank you page or return JSON
            return HttpResponse(f'Payment confirmed for order {order.id}. You can close this window.')
        else:
            order.status = 'failed'
            order.save()
            return HttpResponse(f'Payment failed for order {order.id}.')


@method_decorator(csrf_exempt, name='dispatch')
class CinetPayWebhookView(APIView):
    """Webhook endpoint for CinetPay notifications (development helper).

    NOTE: In production you must verify the signature provided by CinetPay and
    validate the payload (amount, merchant id, etc.). This implementation is a
    permissive helper for sandbox/testing: it accepts JSON or form-encoded
    POSTs containing at least an `order_id` or `transaction_id` and a `status`.
    """
    permission_classes = []

    def post(self, request):
        try:
            payload = request.data if hasattr(request, 'data') else json.loads(request.body)
        except Exception:
            try:
                payload = json.loads(request.body.decode('utf-8'))
            except Exception:
                payload = {}

        order_id = payload.get('order_id') or payload.get('transaction_id')
        status_q = payload.get('status') or payload.get('status_payment') or payload.get('code')

        if not order_id:
            return HttpResponse('missing order_id', status=400)

        try:
            order = Order.objects.get(id=int(order_id))
        except Order.DoesNotExist:
            return HttpResponse('order not found', status=404)

        if str(status_q).lower() in ('success', 'paid', 'ok', '00'):
            order.status = 'paid'
            order.save()
            # clear cart for user if present
            if order.user and hasattr(order.user, 'cart'):
                order.user.cart.items.all().delete()
            return HttpResponse('OK', status=200)
        else:
            order.status = 'failed'
            order.save()
            return HttpResponse('ignored', status=200)
