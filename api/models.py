from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from api.loggers import TransactionApiLogger, OrderLogger


class Wallet(models.Model):
    balance = models.PositiveIntegerField(default=0)
    wallet_address = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="wallet", unique=True, blank=True,
                                null=True)

    def __str__(self):
        return self.user.username + " wallet"


class Order(models.Model):
    class OrderStats(models.TextChoices):
        AWAITING_PAYMENT = 'AWAITING_PAYMENT', _('Awaiting Payment')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        DECLINED = 'DECLINED', _('Declined')
        REFUNDED = 'REFUNDED', _('Refunded')

    class OrderTypes(models.TextChoices):
        DEPOSIT = "DEPOSIT", _("Deposit")
        PURCHASE = "PURCHASE", _("Purchase")

    class PaymentMethods(models.TextChoices):
        WALLET = "WALLET", _("Wallet"),
        BANK = "BANK", _("Bank")

    status = models.CharField(choices=OrderStats)
    type = models.CharField(choices=OrderTypes)
    payment_method = models.CharField(choices=PaymentMethods)
    event_id = models.CharField(max_length=100, blank=True, null=True)
    order_id = models.UUIDField(default=uuid.uuid4)
    Authority = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='orders')
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    purchase_time = models.DateTimeField(null=True, blank=True)
    deposit_time = models.DateTimeField(null=True, blank=True)
    refund_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.order_id)

    def refund(self, commission: int, time_difference):
        commission_price = int(commission * self.amount / 100)
        self.user.deposit(commission_price)
        self.status = self.OrderStats.REFUNDED
        self.save()
        OrderLogger.info(
            f"order refunded successfully, amount of {commission_price} returned to user {self.user.oid}, cancel_time = {self.refund_time}, time_delta = {time_difference}")
        return True


class Transaction(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, blank=True, null=True, related_name='transaction')
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    transaction_id = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    response_code = models.IntegerField(blank=True, null=True)

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

        return f"successfully added {amount} to user {self.oid}, new balance is {self.wallet.balance}"

    def purchase_event(self, event_id: str, amount: int):
        if self.wallet.balance < amount:
            Order.objects.create(status=Order.OrderStats.DECLINED,
                                 type=Order.OrderTypes.PURCHASE,
                                 payment_method=Order.PaymentMethods.WALLET,
                                 event_id=event_id,
                                 amount=amount,
                                 user=self)
            return False
        try:
            order = Order.objects.get(user_id=self.id, event_id=event_id)
            return False
        except Order.DoesNotExist as error:

            order = Order.objects.create(status=Order.OrderStats.COMPLETED,
                                         type=Order.OrderTypes.PURCHASE,
                                         payment_method=Order.PaymentMethods.WALLET,
                                         event_id=event_id,
                                         amount=amount,
                                         user=self)
            current_balance = self.wallet.balance
            new_balance = current_balance - amount
            wallet = self.wallet
            wallet.balance = new_balance
            wallet.save()
            Transaction.objects.create(order=order)
            TransactionApiLogger.info(
                f"successfully purchased event {event_id} to user {self.oid}, new balance is {self.wallet.balance}")
            return True

    def get_balance(self):
        return self.wallet.balance

    def __str__(self):
        return self.username
