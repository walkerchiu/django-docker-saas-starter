import graphene

from account.graphql.dashboard.profile import ProfileMutation, ProfileQuery
from account.graphql.dashboard.user import UserQuery


class Query(
    ProfileQuery,
    UserQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    ProfileMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
