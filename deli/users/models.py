from django.db import models

from locations.models import Area, City, State

from .constants import STEP_CHOICES, ASK_NAME
from restaurants.models import (
    Restaurant,
    Category,
    MenuItem,
)

def default_navigation_stack():
    return ["HOME"]

class Customer(models.Model):

    phone = models.CharField(
        max_length=20,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    is_registered = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def default_address(self):
        return self.addresses.filter(
            is_default=True
        ).first()

    def __str__(self):
        return self.name or self.phone


class ConversationState(models.Model):

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name="conversation",
    )

    current_step = models.CharField(
        max_length=50,
        choices=STEP_CHOICES,
        default=ASK_NAME,
    )

    selected_state = models.ForeignKey(
        State,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    selected_city = models.ForeignKey(
        City,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    selected_area = models.ForeignKey(
        Area,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    selected_restaurant = models.ForeignKey(
    Restaurant,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="+",
    )

    selected_category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    selected_menu_item = models.ForeignKey(
        MenuItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    search_query = models.CharField(
    max_length=255,
    blank=True,
    default="",
    )
    
    search_result_type = models.JSONField(
    max_length=20,
    blank=True,
    default=list,
    )
    
    search_result_ids = models.JSONField(
    default=list,
    blank=True,
    )
    
    restaurant_ids = models.JSONField(
    default=list,
    blank=True,
    )

    last_message = models.TextField(
        blank=True,
    )
    
    navigation_stack = models.JSONField(
    default=default_navigation_stack,
    blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.customer.phone}"
            f" ({self.current_step})"
        )