import graphene

from account.graphql.hq.types.user import UserNode
from core.relay.connection import DjangoFilterConnectionField


class UserMutation(graphene.ObjectType):
    pass


class UserQuery(graphene.ObjectType):
    user = graphene.relay.Node.Field(UserNode)
    users = DjangoFilterConnectionField(
        UserNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
