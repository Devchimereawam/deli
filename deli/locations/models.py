from django.db import models


class State(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):

    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="cities",
    )

    name = models.CharField(
        max_length=100,
    )

    class Meta:
        unique_together = ("state", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class Area(models.Model):

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="areas",
    )

    name = models.CharField(
        max_length=120,
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
    )

    longitude = models.FloatField(
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("city", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.city.name}"


class Address(models.Model):

    HOME = "home"
    WORK = "work"
    SCHOOL = "school"
    OTHER = "other"

    LABELS = [
        (HOME, "Home"),
        (WORK, "Work"),
        (SCHOOL, "School"),
        (OTHER, "Other"),
    ]

    customer = models.ForeignKey(
        "users.Customer",
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    label = models.CharField(
        max_length=20,
        choices=LABELS,
        default=HOME,
    )

    formatted_address = models.TextField(
    blank=True,
    default="",
    )

    landmark = models.CharField(
        max_length=255,
        blank=True,
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
    )

    longitude = models.FloatField(
        null=True,
        blank=True,
    )

    state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    is_default = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    
    @property
    def display_location(self):
        if self.area:
            return self.area.name

        if self.city:
            return self.city.name

        if self.state:
            return self.state.name

        return self.formatted_address

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.customer.phone} - {self.label}"