from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView
from .views import CartView, AddCartItemView, RemoveCartItemView, CheckoutView, PaymentMockView
from .views import CreateStripePaymentIntentView, StripeWebhookView, StripeConfigView
from .views import CreateCinetpayPaymentView, CreateCinetPayTransactionView, CinetPayConfirmView
from .views import CinetPayWebhookView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders-list'),
    path('orders/create/', OrderCreateView.as_view(), name='orders-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='orders-detail'),
    # Cart and checkout
    path('cart/', CartView.as_view(), name='cart-detail'),
    path('cart/add/', AddCartItemView.as_view(), name='cart-add'),
    path('cart/remove/', RemoveCartItemView.as_view(), name='cart-remove'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('pay/mock/', PaymentMockView.as_view(), name='pay-mock'),
    # Stripe
    path('stripe/create-payment-intent/', CreateStripePaymentIntentView.as_view(), name='stripe-create-payment-intent'),
    path('stripe/config/', StripeConfigView.as_view(), name='stripe-config'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('cinetpay/create/', CreateCinetpayPaymentView.as_view(), name='cinetpay-create'),
        path('cinetpay/confirm/', CinetPayConfirmView.as_view(), name='cinetpay-confirm'),
    path('cinetpay/webhook/', CinetPayWebhookView.as_view(), name='cinetpay-webhook'),
]
