from django.db import models
from core.models import BaseModel


class Notification(BaseModel):
    """In-app notification for users."""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"
