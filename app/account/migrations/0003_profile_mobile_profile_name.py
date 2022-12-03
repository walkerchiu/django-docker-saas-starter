# Generated by Django 4.1.3 on 2022-11-21 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_user_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="mobile",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
    ]