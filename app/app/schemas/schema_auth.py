import graphene

from account.graphql.schema_auth import Mutation as AccountMutation
from core.graphql_jwt.relay import ObtainJSONWebToken, Refresh, Revoke, Verify
from tenant.graphql.schema_auth import Mutation as TenantMutation, Query as TenantQuery


class Mutation(
    AccountMutation,
    TenantMutation,
    graphene.ObjectType,
):
    refresh_token = Refresh.Field()
    revoke_token = Revoke.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()


class Query(
    TenantQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
