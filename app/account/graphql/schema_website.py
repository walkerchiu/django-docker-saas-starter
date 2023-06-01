import graphene

from account.graphql.website.profile import ProfileMutation, ProfileQuery
from account.graphql.website.user import UserQuery


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
