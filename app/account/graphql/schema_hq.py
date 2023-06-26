import graphene

from account.graphql.hq.profile import ProfileMutation, ProfileQuery
from account.graphql.hq.user import UserQuery


class Mutation(
    ProfileMutation,
    graphene.ObjectType,
):
    pass


class Query(
    ProfileQuery,
    UserQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
