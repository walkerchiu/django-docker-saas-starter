import graphene

from role.graphql.hq.permission import PermissionMutation, PermissionQuery
from role.graphql.hq.role import RoleMutation, RoleQuery


class Mutation(
    PermissionMutation,
    RoleMutation,
    graphene.ObjectType,
):
    pass


class Query(
    PermissionQuery,
    RoleQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
