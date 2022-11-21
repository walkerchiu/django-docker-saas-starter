from graphql_jwt.decorators import login_required
from graphql.execution.base import ResolveInfo
import graphene

from account.graphql.dashboard.user import UserNode
from account.graphql.schema_dashboard import UserQuery
from role.graphql.schema_dashboard import Mutation as RoleMutation, Query as RoleQuery
from tenant.graphql.schema_dashboard import Query as TenantQuery


class Query(
    RoleQuery,
    TenantQuery,
    UserQuery,
    graphene.ObjectType,
):
    viewer = graphene.Field(UserNode)

    @login_required
    def resolve_viewer(self, info: ResolveInfo, **kwargs):
        return info.context.user


class Mutation(
    RoleMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
