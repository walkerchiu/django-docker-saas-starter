import re

from django.core.exceptions import ValidationError
from django.db import connection, transaction

from django_filters import (
    BooleanFilter,
    CharFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene_django import DjangoObjectType, DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql.execution.base import ResolveInfo
import graphene

from core.relay.connection import ExtendedConnection
from core.types import TaskStatusType
from core.utils import strip_dict
from organization.models import Organization
from role.models import Permission, PermissionTrans


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = (
            "id",
            "slug",
            "is_protected",
        )


class PermissionTransType(DjangoObjectType):
    class Meta:
        model = PermissionTrans
        fields = (
            "language_code",
            "name",
            "description",
        )


class PermissionFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")
    language_code = CharFilter(
        field_name="translations__language_code", lookup_expr="exact"
    )
    name = CharFilter(field_name="translations__name", lookup_expr="icontains")
    description = CharFilter(
        field_name="translations__description", lookup_expr="icontains"
    )
    is_protected = BooleanFilter(field_name="is_protected")
    created_at_gt = DateTimeFilter(field_name="created_at", lookup_expr="gt")
    created_at_gte = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_lt = DateTimeFilter(field_name="created_at", lookup_expr="lt")
    created_at_lte = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_at_gt = DateTimeFilter(field_name="updated_at", lookup_expr="gt")
    updated_at_gte = DateTimeFilter(field_name="updated_at", lookup_expr="gte")
    updated_at_lt = DateTimeFilter(field_name="updated_at", lookup_expr="lt")
    updated_at_lte = DateTimeFilter(field_name="updated_at", lookup_expr="lte")

    class Meta:
        model = Permission
        fields = []

    order_by = OrderingFilter(
        fields=(
            "slug",
            "is_protected",
            ("translations__name", "name"),
            "created_at",
            "updated_at",
        )
    )


class PermissionConnection(graphene.relay.Connection):
    class Meta:
        node = PermissionType


class PermissionNode(DjangoObjectType):
    class Meta:
        model = Permission
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = PermissionFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    translation = graphene.Field(PermissionTransType)
    translations = DjangoListField(PermissionTransType)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            permission = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return permission

    @staticmethod
    def resolve_translation(root: Permission, info: ResolveInfo):
        return root.translations.filter(
            language_code=root.organization.language_code
        ).first()

    @staticmethod
    def resolve_translations(root: Permission, info: ResolveInfo):
        return root.translations


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
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        input = strip_dict(input)
        languageCode = input["languageCode"]
        slug = input["slug"]
        name = input["name"]
        description = input["description"] if "description" in input else None
        isPublished = input["isPublished"] if "isPublished" in input else False
        publishedAt = input["publishedAt"] if "publishedAt" in input else None

        if not languageCode:
            raise ValidationError("The languageCode is invalid!")
        if (
            not slug
            or re.search(r"\W", slug.replace("-", ""))
            or any(str in slug for str in ["\\"])
        ):
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


class DeletePermissions(graphene.relay.ClientIDMutation):
    class Input:
        ids = graphene.List(graphene.ID, required=True)

    success = graphene.Boolean()
    warnings = graphene.Field(TaskStatusType)

    @classmethod
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        input = strip_dict(input)
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

        return DeletePermissions(success=True, warnings=warnings)


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
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        input = strip_dict(input)
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
        if (
            not slug
            or re.search(r"\W", slug.replace("-", ""))
            or any(str in slug for str in ["\\"])
        ):
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

                PermissionTrans.objects.update_or_create(
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


class PermissionQuery(graphene.ObjectType):
    permission = graphene.relay.Node.Field(PermissionNode)
    permissions = DjangoFilterConnectionField(
        PermissionNode, orderBy=graphene.List(of_type=graphene.String)
    )


class PermissionMutation(graphene.ObjectType):
    create_permission = CreatePermission.Field()
    delete_permissions = DeletePermissions.Field()
    update_permission = UpdatePermission.Field()
