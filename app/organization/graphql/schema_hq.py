import graphene

from organization.graphql.hq.organization import OrganizationMutation, OrganizationQuery


class Mutation(
    OrganizationMutation,
    graphene.ObjectType,
):
    pass


class Query(
    OrganizationQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
