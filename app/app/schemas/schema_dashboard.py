from graphql_jwt.decorators import login_required
from graphql.execution.base import ResolveInfo
import graphene

from account.graphql.dashboard.user import UserNode
from account.graphql.schema_dashboard import UserQuery


class Query(
    UserQuery,
    graphene.ObjectType,
):
    viewer = graphene.Field(UserNode)

    @login_required
    def resolve_viewer(self, info: ResolveInfo, **kwargs):
        return info.context.user


class Mutation(
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query)
