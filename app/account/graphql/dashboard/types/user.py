from django.conf import settings

from django_tenants.utils import schema_context
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
import graphene

from account.graphql.dashboard.types.profile import ProfileNode
from account.models import User
from core.relay.connection import ExtendedConnection
from tenant.models import Domain, Tenant


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "last_login",
            "profile",
        )


class UserConnection(graphene.relay.Connection):
    class Meta:
        node = UserType


class TenantsType(graphene.ObjectType):
    domain = graphene.String()


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            "id": ["exact"],
            "email": ["iexact", "icontains", "istartswith"],
            "name": ["iexact", "icontains", "istartswith"],
        }
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        order_by_field = "email"
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    profile = graphene.Field(ProfileNode)
    tenants = graphene.List(TenantsType)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset.select_related("profile")

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            user = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        if info.context.user.id == user.id:
            return user

        raise Exception("Bad Request!")

    @staticmethod
    def resolve_profile(root: User, info, **kwargs):
        return info.context.loaders.profile_by_user_loader.load(root.id)

    @staticmethod
    def resolve_tenants(root: User, info: ResolveInfo):
        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            tenants = []
            email = info.context.user.email
            records = Tenant.objects.filter(email=email)
            for record in records:
                domain = Domain.objects.get(tenant=record, is_builtin=True)
                tenants.append({"domain": domain.domain})
        return tenants
