import graphene

from core.relay.connection import DjangoFilterConnectionField
from tenant.graphql.hq.types.tenant import TenantNode


class TenantMutation(graphene.ObjectType):
    pass


class TenantQuery(graphene.ObjectType):
    tenant = graphene.relay.Node.Field(TenantNode)
    tenants = DjangoFilterConnectionField(
        TenantNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
