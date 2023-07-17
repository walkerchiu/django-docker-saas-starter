from django.core.exceptions import ValidationError
from django.db import connection, transaction

from graphene import ResolveInfo
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
import graphene

from core.decorators import strip_input
from core.helpers.translation_helper import TranslationHelper
from core.types import TaskStatusType
from core.utils import is_slug_invalid
from organization.models import Organization
from role.graphql.hq.types.role import RoleNode, RoleTransInput
from role.models import Role


class CreateRole(graphene.relay.ClientIDMutation):
    class Input:
        slug = graphene.String(required=True)
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()
        translations = graphene.List(graphene.NonNull(RoleTransInput), required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleNode)

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
            label="role",
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

        if Role.objects.filter(organization_id=organization.id, slug=slug).exists():
            raise ValidationError("The slug is already in use!")
        else:
            try:
                role = Role.objects.create(
                    organization_id=organization.id,
                    slug=slug,
                    is_protected=False,
                    is_published=isPublished,
                    published_at=publishedAt,
                )
                for translation in translations:
                    role.translations.create(
                        language_code=translation["language_code"],
                        name=translation["name"],
                        description=translation["description"],
                    )
            except Role.DoesNotExist:
                raise Exception("Can not find this role!")

        return CreateRole(success=True, role=role)


class DeleteRoleBatch(graphene.relay.ClientIDMutation):
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
                _, role_id = from_global_id(id)
            except:
                warnings["error"].append(id)

            try:
                role = Role.objects.only("id").get(pk=role_id, is_protected=True)
                role.delete()

                warnings["done"].append(id)
            except Role.DoesNotExist:
                warnings["not_found"].append(id)

        return DeleteRoleBatch(success=True, warnings=warnings)


class UpdateRole(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        slug = graphene.String(required=True)
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()
        translations = graphene.List(graphene.NonNull(RoleTransInput), required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleNode)

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
            label="role",
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
            _, role_id = from_global_id(id)
        except:
            raise Exception("Bad Request!")

        organization = Organization.objects.only("id").get(
            schema_name=connection.schema_name
        )

        if (
            Role.objects.exclude(pk=role_id)
            .filter(organization_id=organization.id, slug=slug)
            .exists()
        ):
            raise ValidationError("The slug is already in use!")
        else:
            try:
                role = Role.objects.get(
                    pk=role_id, organization_id=organization.id, is_protected=True
                )
                role.slug = slug
                role.is_published = isPublished
                role.published_at = publishedAt
                role.save()

                for translation in translations:
                    role.translations.update_or_create(
                        language_code=translation["language_code"],
                        defaults={
                            "name": translation["name"],
                            "description": translation["description"],
                        },
                    )
            except Role.DoesNotExist:
                raise Exception("Can not find this role!")

        return UpdateRole(success=True, role=role)


class RoleMutation(graphene.ObjectType):
    role_create = CreateRole.Field()
    role_delete_batch = DeleteRoleBatch.Field()
    role_update = UpdateRole.Field()


class RoleQuery(graphene.ObjectType):
    role = graphene.relay.Node.Field(RoleNode)
    roles = DjangoFilterConnectionField(
        RoleNode, orderBy=graphene.List(of_type=graphene.String)
    )
