import graphene

from account.graphql.website.types.user import UserNode


class UserMutation(graphene.ObjectType):
    pass


class UserQuery(graphene.ObjectType):
    user = graphene.relay.Node.Field(UserNode)
