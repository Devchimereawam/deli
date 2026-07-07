import os
from django.db import models
from django.utils.text import slugify

from locations.models import Area


class Restaurant(models.Model):
    name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
    )

    whatsapp_number = models.CharField(
        max_length=20,
    )

    contact_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    cuisine_type = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    description = models.TextField(
        blank=True,
    )

    address = models.TextField()

    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="restaurants",
    )

    logo = models.ImageField(
        upload_to="restaurants/logos/",
        blank=True,
        null=True,
    )

    cover_image = models.ImageField(
        upload_to="restaurants/covers/",
        blank=True,
        null=True,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00,
    )

    total_reviews = models.PositiveIntegerField(
        default=0,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    send_orders_to_deli_dash = models.BooleanField(
        default=False,
        help_text="Use Deli Dash to manually buy from this restaurant instead of messaging the restaurant directly.",
    )

    estimated_prep_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Estimated kitchen preparation time shown to customers and operators.",
    )

    bank_name = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    bank_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    account_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    account_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    nomba_account_ref = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-rating",
            "name",
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def cover_image_url(self):

        if not self.cover_image:
            return None

        base_url = os.getenv("NGROK_URL", "").rstrip("/")

        return f"{base_url}{self.cover_image.url}"


class Category(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    name = models.CharField(
        max_length=120,
    )

    class Meta:
        unique_together = (
            "restaurant",
            "name",
        )

        ordering = [
            "name",
        ]

    def __str__(self):
        return self.name


class MenuItem(models.Model):

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_items",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="menu_items",
    )

    name = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    image = models.ImageField(
        upload_to="menu/",
        blank=True,
        null=True,
    )

    is_available = models.BooleanField(
        default=True,
    )

    is_featured = models.BooleanField(
        default=False,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00,
    )

    total_reviews = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "name",
        ]

    def __str__(self):
        return self.name


class Inventory(models.Model):

    menu_item = models.OneToOneField(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="inventory",
    )

    quantity = models.PositiveIntegerField(
        default=0,
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=5,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def in_stock(self):
        return self.quantity > 0

    def __str__(self):
        return f"{self.menu_item.name} ({self.quantity})"


class OpeningHour(models.Model):

    DAYS = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="opening_hours",
    )

    day = models.CharField(
        max_length=3,
        choices=DAYS,
    )

    opening_time = models.TimeField()

    closing_time = models.TimeField()

    is_closed = models.BooleanField(
        default=False,
    )

    class Meta:
        unique_together = (
            "restaurant",
            "day",
        )

        ordering = [
            "id",
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.day}"


class RestaurantReview(models.Model):

    customer = models.ForeignKey(
        "users.Customer",
        on_delete=models.CASCADE,
        related_name="restaurant_reviews",
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    order = models.OneToOneField(
        "orders.Order",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="review",
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
    )

    comment = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.rating}/5"


class MenuItemReview(models.Model):

    customer = models.ForeignKey(
        "users.Customer",
        on_delete=models.CASCADE,
        related_name="menu_item_reviews",
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    order = models.ForeignKey(
        "orders.Order",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menu_item_reviews",
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
    )

    comment = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.menu_item.name} - {self.rating}/5"
