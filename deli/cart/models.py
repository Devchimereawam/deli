from django.db import models
from decimal import Decimal

from restaurants.models import MenuItem
from users.models import Customer

# Create your models here.
class Cart(models.Model):

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def total_items(self):
        return sum(
            item.quantity
            for item in self.items.all()
        )

    @property
    def subtotal(self):
        return sum(
            item.subtotal
            for item in self.items.select_related(
                "menu_item",
            )
        )

    @property
    def delivery_fee(self):
        """
        Placeholder.

        Will become dynamic in Phase 9.
        """
        return Decimal("1500.00")

    @property
    def total(self):
        return self.subtotal + self.delivery_fee

    def clear(self):

        self.items.all().delete()

    def __str__(self):
        return f"Cart ({self.customer.phone})"


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = (
            "cart",
            "menu_item",
        )

    @property
    def subtotal(self):
        return (
            self.menu_item.price
            * self.quantity
        )

    def __str__(self):
        return (
            f"{self.quantity} × "
            f"{self.menu_item.name}"
        )