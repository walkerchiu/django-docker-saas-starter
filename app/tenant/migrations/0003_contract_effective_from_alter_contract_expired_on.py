# Generated by Django 4.2.3 on 2023-07-15 01:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant", "0002_alter_domain_domain"),
    ]

    operations = [
        migrations.AddField(
            model_name="contract",
            name="effective_from",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="contract",
            name="expired_on",
            field=models.DateTimeField(null=True),
        ),
    ]
