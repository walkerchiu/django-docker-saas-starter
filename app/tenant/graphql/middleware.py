from graphene import ResolveInfo

from core.loaders import generate_loader_for_one_to_many


class DashboardLoaders:
    def __init__(self):
        from tenant.graphql.dashboard.types.contract import ContractNode
        from tenant.graphql.dashboard.types.domain import DomainNode

        self.contracts_by_tenant_loader = generate_loader_for_one_to_many(
            ContractNode, "tenant_id"
        )()
        self.domains_by_tenant_loader = generate_loader_for_one_to_many(
            DomainNode, "tenant_id"
        )()


class LoaderMiddleware:
    def resolve(self, next, root, info: ResolveInfo, **args):
        if info.context.path.startswith("/dashboard/"):
            info.context.loaders = DashboardLoaders()

        return next(root, info, **args)
