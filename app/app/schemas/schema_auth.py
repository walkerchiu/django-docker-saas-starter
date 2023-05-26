from graphene import ResolveInfo
from graphql_jwt.decorators import login_required
import graphene

from account.graphql.auth.types.user import UserNode
from account.graphql.schema_auth import Mutation as AccountMutation
from core.graphql_jwt.relay import ObtainJSONWebToken, Refresh, Revoke, Verify


class Mutation(
    AccountMutation,
    graphene.ObjectType,
):
    refresh_token = Refresh.Field()
    revoke_token = Revoke.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()


class Query(
    graphene.ObjectType,
):
    viewer = graphene.Field(UserNode)

    @login_required
    def resolve_viewer(self, info: ResolveInfo, **kwargs):
        return info.context.user


schema = graphene.Schema(mutation=Mutation, query=Query)
