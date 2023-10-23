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
from organization.graphql.hq.types.organization import (
    OrganizationNode,
    OrganizationTransInput,
)
from organization.models import Organization


class CreateOrganization(graphene.relay.ClientIDMutation):
    class Input:
        slug = graphene.String(required=True)
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()
        translations = graphene.List(
            graphene.NonNull(OrganizationTransInput), required=True
        )

    success = graphene.Boolean()
    organization = graphene.Field(OrganizationNode)

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
            label="organization",
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

        if Organization.objects.filter(
            organization_id=organization.id, slug=slug
        ).exists():
            raise ValidationError("The slug is already in use!")
        else:
            try:
                organization = Organization.objects.create(
                    organization_id=organization.id,
                    slug=slug,
                    is_protected=False,
                    is_published=isPublished,
                    published_at=publishedAt,
                )
                for translation in translations:
                    organization.translations.create(
                        language_code=translation["language_code"],
                        name=translation["name"],
                        description=translation["description"],
                    )
            except Organization.DoesNotExist:
                raise ValidationError("Can not find this organization!")

        return CreateOrganization(success=True, organization=organization)


class DeleteOrganizationBatch(graphene.relay.ClientIDMutation):
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
                _, organization_id = from_global_id(id)
            except:
                warnings["error"].append(id)

            try:
                organization = Organization.objects.only("id").get(
                    pk=organization_id, is_protected=True
                )
                organization.delete()

                warnings["done"].append(id)
            except Organization.DoesNotExist:
                warnings["not_found"].append(id)

        return DeleteOrganizationBatch(success=True, warnings=warnings)


class UpdateOrganization(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        slug = graphene.String(required=True)
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()
        translations = graphene.List(
            graphene.NonNull(OrganizationTransInput), required=True
        )

    success = graphene.Boolean()
    organization = graphene.Field(OrganizationNode)

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
            label="organization",
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
            _, organization_id = from_global_id(id)
        except:
            raise ValidationError("Bad Request!")

        organization = Organization.objects.only("id").get(
            schema_name=connection.schema_name
        )

        if (
            Organization.objects.exclude(pk=organization_id)
            .filter(organization_id=organization.id, slug=slug)
            .exists()
        ):
            raise ValidationError("The slug is already in use!")
        else:
            try:
                organization = Organization.objects.get(
                    pk=organization_id,
                    organization_id=organization.id,
                    is_protected=True,
                )
                organization.slug = slug
                organization.is_published = isPublished
                organization.published_at = publishedAt
                organization.save()

                for translation in translations:
                    organization.translations.update_or_create(
                        language_code=translation["language_code"],
                        defaults={
                            "name": translation["name"],
                            "description": translation["description"],
                        },
                    )
            except Organization.DoesNotExist:
                raise ValidationError("Can not find this organization!")

        return UpdateOrganization(success=True, organization=organization)


class OrganizationMutation(graphene.ObjectType):
    organization_create = CreateOrganization.Field()
    organization_delete_batch = DeleteOrganizationBatch.Field()
    organization_update = UpdateOrganization.Field()


class OrganizationQuery(graphene.ObjectType):
    organization = graphene.relay.Node.Field(OrganizationNode)
    organizations = DjangoFilterConnectionField(
        OrganizationNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
