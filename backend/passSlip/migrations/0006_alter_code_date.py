# Generated by Django 5.1.1 on 2024-09-23 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passSlip', '0005_slip_checkinqr_slip_checkoutqr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='code',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
