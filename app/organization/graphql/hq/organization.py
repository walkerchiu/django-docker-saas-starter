from graphene_django.filter import DjangoFilterConnectionField
import graphene

from organization.graphql.hq.types.organization import OrganizationNode


class OrganizationMutation(graphene.ObjectType):
    pass


class OrganizationQuery(graphene.ObjectType):
    organization = graphene.relay.Node.Field(OrganizationNode)
    organizations = DjangoFilterConnectionField(
        OrganizationNode, orderBy=graphene.List(of_type=graphene.String)
    )
