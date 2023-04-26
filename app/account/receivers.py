from django.dispatch import receiver

from graphene import ResolveInfo

from account.models import User
from account.signals import signin_fail, signin_success


@receiver(signin_fail)
def signin_fail(sender, info: ResolveInfo, user: User, **kwargs):
    print(sender, user.id)


@receiver(signin_success)
def signin_success(sender, info: ResolveInfo, user: User, **kwargs):
    print(sender, user.id)
