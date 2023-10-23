from django.core.exceptions import ValidationError
from django.db import connection, transaction

from graphene import ResolveInfo
from graphql_relay import from_global_id
import graphene

from core.decorators import strip_input
from core.helpers.translation_helper import TranslationHelper
from core.relay.connection import DjangoFilterConnectionField
from core.types import TaskStatusType
from core.utils import is_slug_invalid
from organization.models import Organization
from role.graphql.hq.types.permission import PermissionNode, PermissionTransInput
from role.models import Permission


class CreatePermission(graphene.relay.ClientIDMutation):
    class Input:
        slug = graphene.String(required=True)
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()
        translations = graphene.List(
            graphene.NonNull(PermissionTransInput), required=True
        )

    success = graphene.Boolean()
    permission = graphene.Field(PermissionNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        slug = input["slug"]
        isPublished = input["isPublished"] if "isPublished" in input else False
        publishedAt = input["publishedAt"] if "publishedAt" in input else None
        translations = input["translations"]

        translation_helper = TranslationHelper()
        result, message = translation_helper.validate_translations_from_input(
            label="permission",
            translations=translations,
            required=True,
            default_language_required=False,
        )
        if not result:
            raise ValidationError(message)

        if is_slug_invalid(slug):
            raise ValidationError("The slug is invalid!")

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
                for translation in translations:
                    permission.translations.create(
                        language_code=translation["language_code"],
                        name=translation["name"],
                        description=translation["description"],
                    )
            except Permission.DoesNotExist:
                raise ValidationError("Can not find this permission!")

        return CreatePermission(success=True, permission=permission)


class DeletePermissionBatch(graphene.relay.ClientIDMutation):
    class Input:
        idList = graphene.List(graphene.ID, required=True)

    success = graphene.Boolean()
    warnings = graphene.Field(TaskStatusType)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        id_list = input["idList"] if "idList" in input else []

        warnings = {
            "done": [],
            "error": [],
            "in_protected": [],
            "in_use": [],
            "not_found": [],
            "wait_to_do": [],
        }

        for id in id_list:
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
        slug = graphene.String(required=True)
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()
        translations = graphene.List(
            graphene.NonNull(PermissionTransInput), required=True
        )

    success = graphene.Boolean()
    permission = graphene.Field(PermissionNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        id = input["id"]
        slug = input["slug"]
        isPublished = input["isPublished"] if "isPublished" in input else False
        publishedAt = input["publishedAt"] if "publishedAt" in input else None
        translations = input["translations"]

        translation_helper = TranslationHelper()
        result, message = translation_helper.validate_translations_from_input(
            label="permission",
            translations=translations,
            required=True,
            default_language_required=False,
        )
        if not result:
            raise ValidationError(message)

        if not id:
            raise ValidationError("The id is invalid!")
        if is_slug_invalid(slug):
            raise ValidationError("The slug is invalid!")

        try:
            _, permission_id = from_global_id(id)
        except:
            raise ValidationError("Bad Request!")

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

                for translation in translations:
                    permission.translations.update_or_create(
                        language_code=translation["language_code"],
                        defaults={
                            "name": translation["name"],
                            "description": translation["description"],
                        },
                    )
            except Permission.DoesNotExist:
                raise ValidationError("Can not find this permission!")

        return UpdatePermission(success=True, permission=permission)


class PermissionMutation(graphene.ObjectType):
    permission_create = CreatePermission.Field()
    permission_delete_batch = DeletePermissionBatch.Field()
    permission_update = UpdatePermission.Field()


class PermissionQuery(graphene.ObjectType):
    permission = graphene.relay.Node.Field(PermissionNode)
    permissions = DjangoFilterConnectionField(
        PermissionNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
