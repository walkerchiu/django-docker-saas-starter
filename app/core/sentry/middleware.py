from graphene import ResolveInfo
from sentry_sdk import capture_exception


class SentryMiddleware(object):
    def on_error(self, error):
        capture_exception(error)
        raise error

    def resolve(self, next, root, info: ResolveInfo, **args):
        return next(root, info, **args).catch(self.on_error)
