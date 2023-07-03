from django.core.exceptions import ValidationError
from django.db import connection, transaction

from graphene import ResolveInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
import graphene

from core.decorators import strip_input
from core.types import TaskStatusType
from core.utils import is_slug_invalid
from organization.models import Organization
from role.graphql.dashboard.types.permission import PermissionNode
from role.models import Permission, PermissionTrans


class CreatePermission(graphene.relay.ClientIDMutation):
    class Input:
        languageCode = graphene.String(required=True)
        slug = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()

    success = graphene.Boolean()
    permission = graphene.Field(PermissionNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        languageCode = input["languageCode"]
        slug = input["slug"]
        name = input["name"]
        description = input["description"] if "description" in input else None
        isPublished = input["isPublished"] if "isPublished" in input else False
        publishedAt = input["publishedAt"] if "publishedAt" in input else None

        if not languageCode:
            raise ValidationError("The languageCode is invalid!")
        if is_slug_invalid(slug):
            raise ValidationError("The slug is invalid!")
        if not name:
            raise ValidationError("The name is invalid!")

        organization = Organization.objects.only("id").get(
            schema_name=connection.schema_name
        )

        if Permission.objects.filter(
            organization_id=organization.id, slug=slug
        ).exists():
            raise ValidationError("The slug is already in use!")
        else:
            try:
                permission = Permission.objects.create(
                    organization_id=organization.id,
                    slug=slug,
                    is_protected=False,
                    is_published=isPublished,
                    published_at=publishedAt,
                )
                permission.translations.create(
                    language_code=languageCode,
                    name=name,
                    description=description,
                )
            except Permission.DoesNotExist:
                raise Exception("Can not find this permission!")

        return CreatePermission(success=True, permission=permission)


class DeletePermissionBatch(graphene.relay.ClientIDMutation):
    class Input:
        ids = graphene.List(graphene.ID, required=True)

    success = graphene.Boolean()
    warnings = graphene.Field(TaskStatusType)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        ids = input["ids"] if "ids" in input else []

        warnings = {
            "done": [],
            "error": [],
            "in_protected": [],
            "in_use": [],
            "not_found": [],
            "wait_to_do": [],
        }

        for id in ids:
            try:
                _, permission_id = from_global_id(id)
            except:
                warnings["error"].append(id)

            try:
                permission = Permission.objects.only("id").get(
                    pk=permission_id, is_protected=True
                )
                permission.delete()

                warnings["done"].append(id)
            except Permission.DoesNotExist:
                warnings["not_found"].append(id)

        return DeletePermissionBatch(success=True, warnings=warnings)


class UpdatePermission(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        languageCode = graphene.String(required=True)
        slug = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()

    success = graphene.Boolean()
    permission = graphene.Field(PermissionNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        id = input["id"]
        languageCode = input["languageCode"]
        slug = input["slug"]
        name = input["name"]
        description = input["description"] if "description" in input else None
        isPublished = input["isPublished"] if "isPublished" in input else False
        publishedAt = input["publishedAt"] if "publishedAt" in input else None

        if not id:
            raise ValidationError("The id is invalid!")
        if not languageCode:
            raise ValidationError("The languageCode is invalid!")
        if is_slug_invalid(slug):
            raise ValidationError("The slug is invalid!")
        if not name:
            raise ValidationError("The name is invalid!")

        try:
            _, permission_id = from_global_id(id)
        except:
            raise Exception("Bad Request!")

        organization = Organization.objects.only("id").get(
            schema_name=connection.schema_name
        )

        if (
            Permission.objects.exclude(pk=permission_id)
            .filter(organization_id=organization.id, slug=slug)
            .exists()
        ):
            raise ValidationError("The slug is already in use!")
        else:
            try:
                permission = Permission.objects.get(
                    pk=permission_id, organization_id=organization.id, is_protected=True
                )
                permission.slug = slug
                permission.is_published = isPublished
                permission.published_at = publishedAt
                permission.save()

                permission.translations.update_or_create(
                    permission=permission,
                    language_code=languageCode,
                    defaults={
                        "language_code": languageCode,
                        "name": name,
                        "description": description,
                    },
                )
            except Permission.DoesNotExist:
                raise Exception("Can not find this permission!")

        return UpdatePermission(success=True, permission=permission)


class PermissionMutation(graphene.ObjectType):
    permission_create = CreatePermission.Field()
    permission_delete_batch = DeletePermissionBatch.Field()
    permission_update = UpdatePermission.Field()


class PermissionQuery(graphene.ObjectType):
    permission = graphene.relay.Node.Field(PermissionNode)
    permissions = DjangoFilterConnectionField(
        PermissionNode, orderBy=graphene.List(of_type=graphene.String)
    )
