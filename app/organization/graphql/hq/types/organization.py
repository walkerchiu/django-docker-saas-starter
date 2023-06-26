from django_filters import (
    CharFilter,
    DateTimeFilter,
    FilterSet,
    OrderingFilter,
)
from graphene import ResolveInfo
from graphene_django import DjangoListField, DjangoObjectType
from graphql_jwt.decorators import login_required
import graphene

from core.relay.connection import ExtendedConnection
from organization.models import Organization, OrganizationTrans


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        fields = (
            "id",
            "language_code",
            "is_published",
            "published_at",
        )


class OrganizationConnection(graphene.relay.Connection):
    class Meta:
        node = OrganizationType


class OrganizationTransType(DjangoObjectType):
    class Meta:
        model = OrganizationTrans
        fields = (
            "language_code",
            "name",
            "description",
        )


class OrganizationFilter(FilterSet):
    language_code = CharFilter(
        field_name="translations__language_code", lookup_expr="exact"
    )
    name = CharFilter(field_name="translations__name", lookup_expr="icontains")
    description = CharFilter(
        field_name="translations__description", lookup_expr="icontains"
    )
    created_at_gt = DateTimeFilter(field_name="created_at", lookup_expr="gt")
    created_at_gte = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_lt = DateTimeFilter(field_name="created_at", lookup_expr="lt")
    created_at_lte = DateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_at_gt = DateTimeFilter(field_name="updated_at", lookup_expr="gt")
    updated_at_gte = DateTimeFilter(field_name="updated_at", lookup_expr="gte")
    updated_at_lt = DateTimeFilter(field_name="updated_at", lookup_expr="lt")
    updated_at_lte = DateTimeFilter(field_name="updated_at", lookup_expr="lte")

    class Meta:
        model = Organization
        fields = []

    order_by = OrderingFilter(
        fields=(
            ("translations__name", "name"),
            "created_at",
            "updated_at",
        )
    )


class OrganizationNode(DjangoObjectType):
    class Meta:
        model = Organization
        exclude = (
            "schema_name",
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = OrganizationFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    translation = graphene.Field(OrganizationTransType)
    translations = DjangoListField(OrganizationTransType)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset

    @classmethod
    @login_required
    def get_node(cls, info: ResolveInfo, id):
        try:
            organization = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return organization

    @staticmethod
    def resolve_translation(root: Organization, info: ResolveInfo):
        return root.translations.filter(language_code=root.language_code).first()

    @staticmethod
    def resolve_translations(root: Organization, info: ResolveInfo):
        return root.translations
