# Generated by Django 5.0.2 on 2024-02-18 21:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_remove_transaction_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='response_code',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='order',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='api.order'),
        ),
    ]
