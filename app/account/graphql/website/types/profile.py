from graphene import ResolveInfo
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
import graphene

from account.models import Profile


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "name",
            "mobile",
            "birth",
        )


class ProfileConnection(graphene.relay.Connection):
    class Meta:
        node = ProfileType


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            "id": ["exact"],
            "name": ["iexact", "icontains", "istartswith"],
            "mobile": ["icontains", "istartswith"],
        }
        exclude = (
            "deleted",
            "deleted_by_cascade",
        )
        order_by_field = "id"
        interfaces = (graphene.relay.Node,)

    @classmethod
    @login_required
    def get_queryset(cls, queryset, info: ResolveInfo):
        raise Exception("This operation is not allowed!")

    @classmethod
    @login_required
    def get_node(cls, info: ResolveInfo, id):
        try:
            profile = cls._meta.model.objects.get(pk=id, user_id=info.context.user.id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        return profile
