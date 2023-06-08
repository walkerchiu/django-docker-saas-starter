from graphene import ResolveInfo
from graphql_jwt.decorators import login_required
import graphene

from account.graphql.schema_website import (
    Mutation as AccountMutation,
    Query as AccountQuery,
)
from account.graphql.website.types.user import UserNode
from organization.graphql.schema_dashboard import Query as OrganizationQuery


class Mutation(
    AccountMutation,
    graphene.ObjectType,
):
    pass


class Query(
    AccountQuery,
    OrganizationQuery,
    graphene.ObjectType,
):
    viewer = graphene.Field(UserNode)

    @login_required
    def resolve_viewer(self, info: ResolveInfo, **kwargs):
        return info.context.user


schema = graphene.Schema(mutation=Mutation, query=Query)
