from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from api.models import User, Wallet


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
