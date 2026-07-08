from django.urls import path

from . import views

urlpatterns = [
    path(
        "return/<str:reference>/",
        views.payment_return,
        name="payment-return-reference",
    ),
    path(
        "return/",
        views.payment_return,
        name="payment-return",
    ),
    path(
        "webhooks/nomba/",
        views.nomba_webhook,
        name="nomba-webhook",
    ),
]
