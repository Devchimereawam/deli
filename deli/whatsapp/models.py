from django.db import models

# Create your models here.
class ProcessedMessage(models.Model):

    whatsapp_message_id = models.CharField(
        max_length=255,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.whatsapp_message_id