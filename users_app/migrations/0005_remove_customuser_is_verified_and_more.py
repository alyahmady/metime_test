# Generated by Django 4.1.4 on 2023-01-04 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users_app", "0004_customuser_last_password_change"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="is_verified",
        ),
        migrations.AddField(
            model_name="customuser",
            name="is_email_verified",
            field=models.BooleanField(default=False, verbose_name="Is Email Verified"),
        ),
        migrations.AddField(
            model_name="customuser",
            name="is_phone_verified",
            field=models.BooleanField(default=False, verbose_name="Is Phone Verified"),
        ),
    ]
