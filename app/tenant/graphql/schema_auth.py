import graphene

from tenant.graphql.auth.tenant import TenantMutation, TenantQuery


class Mutation(
    TenantMutation,
    graphene.ObjectType,
):
    pass


class Query(
    TenantQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
