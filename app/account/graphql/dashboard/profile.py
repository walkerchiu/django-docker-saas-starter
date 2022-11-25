from graphene_django.filter import DjangoFilterConnectionField
import graphene

from account.graphql.dashboard.types.profile import ProfileNode


class ProfileQuery(graphene.ObjectType):
    profile = graphene.relay.Node.Field(ProfileNode)
    profiles = DjangoFilterConnectionField(
        ProfileNode, orderBy=graphene.List(of_type=graphene.String)
    )


class ProfileMutation(graphene.ObjectType):
    pass
