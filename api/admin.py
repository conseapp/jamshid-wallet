from django.contrib import admin
from api.models import User, Wallet, Transaction, Order


# Register your models here.

class WalletAdmin(admin.StackedInline):
    model = Wallet
    readonly_fields = ('balance',)
    can_delete = False
    fk_name = 'user'


class OrderInline(admin.TabularInline):
    model = Order
    fields = ['order_id','modified_at','payment_method', 'amount', 'type','status', 'event_id','transaction_id']  # Add fields you want to display
    fk_name = 'user'
    readonly_fields = ['order_id','modified_at','payment_method', 'amount', 'type','status', 'event_id','transaction_id']
    can_delete = False
    extra = 0

    def transaction_id(self,obj):
        return obj.transaction.transaction_id


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('oid', 'username', 'phone')
    list_display = ['oid', 'username', 'phone', 'balance']
    list_display_links = ["oid", "username", "phone"]
    inlines = [WalletAdmin, OrderInline]

    def balance(self, obj):
        return obj.wallet.balance


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('order_id', 'payment_method', 'status', 'type', 'user', 'event_id', 'amount', 'Authority')
    list_display = ('order_id', 'status', 'type', 'user', 'event_id', 'amount', 'created_at')
    list_filter = ('user', 'type', 'status')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('transaction_id', 'user', 'type', 'amount', 'order', 'ref_id', 'response_code')
    list_display = ['transaction_id', 'user', 'type', 'amount', 'order', 'created_at']
    list_filter = ['order__type', 'order__user']

    def user(self, obj):
        return obj.order.user

    def amount(self, obj):
        return obj.order.amount

    def type(self, obj):
        return obj.order.type
