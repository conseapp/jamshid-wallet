from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from api.loggers import TransactionApiLogger


# Create your models here.
class Wallet(models.Model):
    balance = models.IntegerField(default=0)
    wallet_address = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="wallet", unique=True, null=True)

    def __str__(self):
        return self.user.username + " wallet"


class Order(models.Model):
    class OrderStats(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        AWAITING_PAYMENT = 'AWAITING_PAYMENT', _('Awaiting Payment')
        AWAITING_FULFILLMENT = 'AWAITING_FULFILLMENT', _('Awaiting Fulfillment')
        AWAITING_SHIPMENT = 'AWAITING_SHIPMENT', _('Awaiting Shipment')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        DECLINED = 'DECLINED', _('Declined')
        REFUNDED = 'REFUNDED', _('Refunded')

    class OrderTypes(models.TextChoices):
        EVENT = 'EVENT', _('Event')

    status = models.CharField(choices=OrderStats)
    type = models.CharField(choices=OrderTypes)
    event_id = models.CharField(max_length=100)
    order_id = models.UUIDField(default=uuid.uuid4)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='orders')
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_id)


class Transaction(models.Model):
    class TransactionTypes(models.TextChoices):
        DEPOSIT = "DEPOSIT", _("Deposit")
        WITHDRAW = "WITHDRAW", _("Withdraw")
        PURCHASE = "PURCHASE", _("Purchase")

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    type = models.CharField(choices=TransactionTypes)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField()
    stripe_id = models.CharField(max_length=50, null=True)
    transaction_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.transaction_id)


class User(models.Model):
    oid = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def deposit(self, amount: int):
        current_balance = self.wallet.balance
        new_balance = current_balance + amount
        wallet = self.wallet
        wallet.balance = new_balance
        wallet.save()
        Transaction.objects.create(user=self, type=Transaction.TransactionTypes.DEPOSIT, amount=amount)
        TransactionApiLogger.info(
            f"successfully added {amount} to user {self.oid}, new balance is {self.wallet.balance}")
        return True

    def purchase_event(self, event_id: str, amount: int):
        order = Order.objects.create(status=Order.OrderStats.COMPLETED, type=Order.OrderTypes.EVENT, event_id=event_id,
                                     amount=amount, user=self)
        current_balance = self.wallet.balance
        new_balance = current_balance - amount
        wallet = self.wallet
        wallet.balance = new_balance
        wallet.save()
        Transaction.objects.create(user=self, type=Transaction.TransactionTypes.PURCHASE, amount=amount, order=order)
        TransactionApiLogger.info(
            f"successfully purchased event {event_id} to user {self.oid}, new balance is {self.wallet.balance}")

    def get_balance(self):
        return self.wallet.balance

    def __str__(self):
        return self.username

    # def save(self, *args, **kwargs):
    #     created = not self.id
    #     super().save(*args, **kwargs)
    #     if created:
    #         self.wallet = Wallet.objects.create()
