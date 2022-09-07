from graphql_jwt.decorators import login_required
import graphene

from account.graphql.dashboard.user import UserNode
from account.graphql.schema_dashboard import UserQuery


class Query(
    UserQuery,
    graphene.ObjectType,
):
    viewer = graphene.Field(UserNode)

    @login_required
    def resolve_viewer(self, info, **kwargs):
        return info.context.user


class Mutation(
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query)
