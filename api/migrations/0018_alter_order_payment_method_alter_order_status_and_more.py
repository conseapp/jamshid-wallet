# Generated by Django 5.0.2 on 2024-02-24 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_alter_order_authority_alter_order_event_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('WALLET', 'Wallet'), ('BANK', 'Bank')], max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('AWAITING_PAYMENT', 'Awaiting Payment'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('DECLINED', 'Declined'), ('REFUNDED', 'Refunded')], max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='type',
            field=models.CharField(choices=[('DEPOSIT', 'Deposit'), ('PURCHASE', 'Purchase')], max_length=20),
        ),
    ]
