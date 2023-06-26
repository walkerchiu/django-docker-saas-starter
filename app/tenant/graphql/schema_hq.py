import graphene

from tenant.graphql.hq.contract import ContractMutation, ContractQuery
from tenant.graphql.hq.domain import DomainMutation, DomainQuery
from tenant.graphql.hq.tenant import TenantMutation, TenantQuery


class Mutation(
    ContractMutation,
    DomainMutation,
    TenantMutation,
    graphene.ObjectType,
):
    pass


class Query(
    ContractQuery,
    DomainQuery,
    TenantQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
