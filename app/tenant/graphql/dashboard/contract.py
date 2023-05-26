from graphene_django.filter import DjangoFilterConnectionField
import graphene

from tenant.graphql.dashboard.types.contract import ContractNode


class ContractMutation(graphene.ObjectType):
    pass


class ContractQuery(graphene.ObjectType):
    contract = graphene.relay.Node.Field(ContractNode)
    contracts = DjangoFilterConnectionField(
        ContractNode, orderBy=graphene.List(of_type=graphene.String)
    )
