import graphene

from core.graphql_jwt.relay import ObtainJSONWebToken, Refresh, Revoke, Verify


class Query(
    graphene.ObjectType,
):
    pass


class Mutation(
    graphene.ObjectType,
):
    refresh_token = Refresh.Field()
    revoke_token = Revoke.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()


schema = graphene.Schema(mutation=Mutation)
