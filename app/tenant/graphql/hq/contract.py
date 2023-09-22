import graphene

from core.relay.connection import DjangoFilterConnectionField
from tenant.graphql.hq.types.contract import ContractNode


class ContractMutation(graphene.ObjectType):
    pass


class ContractQuery(graphene.ObjectType):
    contract = graphene.relay.Node.Field(ContractNode)
    contracts = DjangoFilterConnectionField(
        ContractNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
