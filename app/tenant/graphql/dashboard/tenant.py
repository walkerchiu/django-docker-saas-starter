import graphene

from tenant.graphql.dashboard.types.tenant import TenantNode


class TenantMutation(graphene.ObjectType):
    pass


class TenantQuery(graphene.ObjectType):
    tenant = graphene.relay.Node.Field(TenantNode)
