import graphene

from tenant.graphql.dashboard.contract import ContractQuery
from tenant.graphql.dashboard.domain import DomainQuery
from tenant.graphql.dashboard.tenant import TenantQuery


class Query(
    ContractQuery,
    DomainQuery,
    TenantQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query)
