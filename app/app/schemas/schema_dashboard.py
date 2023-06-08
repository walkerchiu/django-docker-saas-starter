from graphene import ResolveInfo
from graphql_jwt.decorators import login_required
import graphene

from account.graphql.dashboard.types.user import UserNode
from account.graphql.schema_dashboard import (
    Mutation as AccountMutation,
    Query as AccountQuery,
)
from organization.graphql.schema_dashboard import (
    Mutation as OrganizationMutation,
    Query as OrganizationQuery,
)
from role.graphql.schema_dashboard import Mutation as RoleMutation, Query as RoleQuery
from tenant.graphql.schema_dashboard import (
    Mutation as TenantMutation,
    Query as TenantQuery,
)


class Mutation(
    AccountMutation,
    OrganizationMutation,
    RoleMutation,
    TenantMutation,
    graphene.ObjectType,
):
    pass


class Query(
    AccountQuery,
    OrganizationQuery,
    RoleQuery,
    TenantQuery,
    graphene.ObjectType,
):
    viewer = graphene.Field(UserNode)

    @login_required
    def resolve_viewer(self, info: ResolveInfo, **kwargs):
        return info.context.user


schema = graphene.Schema(mutation=Mutation, query=Query)
