from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from api.models import User, Wallet, Order
from django.utils import timezone


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


@receiver(post_save, sender=Order)
def update_wallet(sender, instance, created, **kwargs):
    if instance.status == Order.OrderStats.COMPLETED and instance.type == Order.OrderTypes.DEPOSIT:
        instance.user.deposit(instance.amount)
        if not instance.deposit_time:
            instance.deposit_time = timezone.localtime()

    if instance.status == Order.OrderStats.COMPLETED and instance.type == Order.OrderTypes.PURCHASE:
        if not instance.purchase_time:
            instance.purchase_time = timezone.localtime()

    if instance.status == Order.OrderStats.REFUNDED:
        if not instance.refund_time:
            instance.refund_time = timezone.localtime()
