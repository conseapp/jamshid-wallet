from django.contrib import admin
from api.models import User, Wallet, Transaction, Order


# Register your models here.

class WalletAdmin(admin.StackedInline):
    model = Wallet
    fk_name = 'user'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('oid', 'username', 'phone')
    list_display = ['oid', 'username', 'phone', 'balance']
    list_display_links = ["oid", "username", "phone"]
    inlines = [WalletAdmin]

    def balance(self, obj):
        return obj.wallet.balance


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('order_id', 'status', 'type', 'user', 'event_id', 'amount')
    list_display = ('order_id', 'status', 'type', 'user', 'event_id', 'amount', 'created_at')
    list_filter = ('user', 'type', 'status')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('transaction_id', 'user', 'type', 'amount', 'order', 'stripe_id')
    list_display = ['transaction_id', 'user', 'type', 'amount', 'order', 'created_at']
    list_filter = ['type', 'user']
