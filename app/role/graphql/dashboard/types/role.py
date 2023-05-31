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
from role.graphql.dashboard.types.permission import PermissionType
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
