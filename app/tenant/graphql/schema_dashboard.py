import graphene

from tenant.graphql.dashboard.contract import ContractQuery
from tenant.graphql.dashboard.domain import DomainMutation, DomainQuery
from tenant.graphql.dashboard.tenant import TenantQuery


class Query(
    ContractQuery,
    DomainQuery,
    TenantQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    DomainMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
