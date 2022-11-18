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
from role.graphql.dashboard.permission import PermissionType
from role.models import Role, RoleTrans


class RoleType(DjangoObjectType):
    class Meta:
        model = Role
        fields = (
            "id",
            "slug",
            "is_protected",
        )


class RoleTransType(DjangoObjectType):
    class Meta:
        model = RoleTrans
        fields = (
            "language_code",
            "name",
            "description",
        )


class RoleFilter(FilterSet):
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
        model = Role
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


class RoleConnection(graphene.relay.Connection):
    class Meta:
        node = RoleType


class RoleNode(DjangoObjectType):
    class Meta:
        model = Role
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = RoleFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    permissions = DjangoListField(PermissionType)
    translation = graphene.Field(RoleTransType)
    translations = DjangoListField(RoleTransType)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            role = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return role

    @staticmethod
    def resolve_translation(root: Role, info: ResolveInfo):
        return root.translations.filter(
            language_code=root.organization.language_code
        ).first()

    @staticmethod
    def resolve_translations(root: Role, info: ResolveInfo):
        return root.translations


class CreateRole(graphene.relay.ClientIDMutation):
    class Input:
        languageCode = graphene.String(required=True)
        slug = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()

    success = graphene.Boolean()
    role = graphene.Field(RoleNode)

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
                role.translations.create(
                    language_code=languageCode,
                    name=name,
                    description=description,
                )
            except Role.DoesNotExist:
                raise Exception("Can not find this role!")

        return CreateRole(success=True, role=role)


class DeleteRoles(graphene.relay.ClientIDMutation):
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
                _, role_id = from_global_id(id)
            except:
                warnings["error"].append(id)

            try:
                role = Role.objects.only("id").get(pk=role_id, is_protected=True)
                role.delete()

                warnings["done"].append(id)
            except Role.DoesNotExist:
                warnings["not_found"].append(id)

        return DeleteRoles(success=True, warnings=warnings)


class UpdateRole(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        languageCode = graphene.String(required=True)
        slug = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()

    success = graphene.Boolean()
    role = graphene.Field(RoleNode)

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

                RoleTrans.objects.update_or_create(
                    role=role,
                    language_code=languageCode,
                    defaults={
                        "language_code": languageCode,
                        "name": name,
                        "description": description,
                    },
                )
            except Role.DoesNotExist:
                raise Exception("Can not find this role!")

        return UpdateRole(success=True, role=role)


class RoleQuery(graphene.ObjectType):
    role = graphene.relay.Node.Field(RoleNode)
    roles = DjangoFilterConnectionField(
        RoleNode, orderBy=graphene.List(of_type=graphene.String)
    )


class RoleMutation(graphene.ObjectType):
    create_role = CreateRole.Field()
    delete_roles = DeleteRoles.Field()
    update_role = UpdateRole.Field()
