from django_filters import (
    BooleanFilter,
    CharFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene import ResolveInfo
from graphene_django import DjangoListField, DjangoObjectType
import graphene

from core.relay.connection import ExtendedConnection
from core.types import TransTypeInput
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


class PermissionTransInput(TransTypeInput):
    name = graphene.String()
    description = graphene.String()


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
