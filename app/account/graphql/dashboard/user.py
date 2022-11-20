from graphene_django.filter import DjangoFilterConnectionField
import graphene

from account.graphql.dashboard.types.user import UserNode


class UserQuery(graphene.ObjectType):
    user = graphene.relay.Node.Field(UserNode)
    users = DjangoFilterConnectionField(
        UserNode, orderBy=graphene.List(of_type=graphene.String)
    )


class UserMutation(graphene.ObjectType):
    pass
