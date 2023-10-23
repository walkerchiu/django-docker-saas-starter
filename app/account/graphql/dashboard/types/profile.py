from django.core.exceptions import ValidationError

from graphene_django import DjangoObjectType
from graphene import ResolveInfo
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
    def get_queryset(cls, queryset, info: ResolveInfo):
        return queryset

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        try:
            profile = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise ValidationError("Bad Request!")

        return profile


class ProfileConnection(graphene.relay.Connection):
    class Meta:
        node = ProfileType
