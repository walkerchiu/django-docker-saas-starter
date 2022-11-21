from graphene_django.filter import DjangoFilterConnectionField
import graphene

from tenant.graphql.dashboard.types.domain import DomainNode


class DomainQuery(graphene.ObjectType):
    domain = graphene.relay.Node.Field(DomainNode)
    domains = DjangoFilterConnectionField(
        DomainNode, orderBy=graphene.List(of_type=graphene.String)
    )


class DomainMutation(graphene.ObjectType):
    pass
