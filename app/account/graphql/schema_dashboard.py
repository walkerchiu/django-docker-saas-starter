import graphene

from account.graphql.dashboard.profile import ProfileQuery
from account.graphql.dashboard.user import UserQuery


class Query(
    ProfileQuery,
    UserQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query)
