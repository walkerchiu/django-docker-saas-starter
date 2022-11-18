import graphene


class TaskStatusType(graphene.ObjectType):
    done = graphene.List(graphene.String)
    error = graphene.List(graphene.String)
    in_protected = graphene.List(graphene.String)
    in_use = graphene.List(graphene.String)
    not_found = graphene.List(graphene.String)
    wait_to_do = graphene.List(graphene.String)
