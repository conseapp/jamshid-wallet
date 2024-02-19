from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from api.models import User, Wallet, Order


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


@receiver(post_save, sender=Order)
def update_wallet(sender, instance, created, **kwargs):
    if instance.status == Order.OrderStats.COMPLETED and instance.type == Order.OrderTypes.DEPOSIT:
        instance.user.deposit(instance.amount)