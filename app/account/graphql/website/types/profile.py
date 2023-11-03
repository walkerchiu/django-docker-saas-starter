from django.core.exceptions import ValidationError

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
        raise ValidationError("This operation is not allowed!")

    @classmethod
    @login_required
    def get_node(cls, info: ResolveInfo, id):
        return cls._meta.model.objects.filter(pk=id).first()


class ProfileConnection(graphene.relay.Connection):
    class Meta:
        node = ProfileType
