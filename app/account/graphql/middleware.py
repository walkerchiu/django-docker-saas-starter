from graphene import ResolveInfo

from account.graphql.loaders import generate_loader_for_one_to_one


class DashboardLoaders:
    def __init__(self):
        from account.graphql.dashboard.types.profile import ProfileNode

        self.profile_by_user_loader = generate_loader_for_one_to_one(
            ProfileNode, "id"
        )()


class LoaderMiddleware:
    def resolve(self, next, root, info: ResolveInfo, **args):
        if info.context.path.startswith("/dashboard/"):
            info.context.loaders = DashboardLoaders()

        return next(root, info, **args)
