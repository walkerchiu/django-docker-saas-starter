# Generated by Django 4.1.3 on 2022-11-11 00:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "deleted",
                    models.DateTimeField(db_index=True, editable=False, null=True),
                ),
                (
                    "deleted_by_cascade",
                    models.BooleanField(default=False, editable=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_published", models.BooleanField(default=False)),
                ("published_at", models.DateField(null=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("schema_name", models.CharField(db_index=True, max_length=32)),
                ("language_code", models.CharField(default="zh-TW", max_length=35)),
            ],
            options={
                "db_table": "app_organization_organization",
                "ordering": ["language_code"],
            },
        ),
        migrations.CreateModel(
            name="OrganizationTrans",
            fields=[
                (
                    "deleted",
                    models.DateTimeField(db_index=True, editable=False, null=True),
                ),
                (
                    "deleted_by_cascade",
                    models.BooleanField(default=False, editable=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("language_code", models.CharField(default="zh-TW", max_length=35)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "organization",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="organization.organization",
                    ),
                ),
            ],
            options={
                "db_table": "app_organization_organization_trans",
                "ordering": ["language_code"],
                "index_together": {("language_code", "organization")},
            },
        ),
    ]