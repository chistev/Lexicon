from django.db import models
from django.contrib.auth.models import User

class NewsletterSubscription(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='newsletter_subscription',
        null=True,  # Allow null for logged-out users
        blank=True
    )
    email = models.EmailField()
    is_subscribed = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.CharField(max_length=100, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {'Subscribed' if self.is_subscribed else 'Unsubscribed'}"

    class Meta:
        ordering = ['-created_at']