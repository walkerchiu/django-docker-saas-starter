from django.core.exceptions import ValidationError
from django.db import transaction

from graphene import ResolveInfo
import graphene

from account.graphql.auth.types.user import UserNode
from account.models import User
from account.services.user_service import UserService
from account.variables.protected_email import PROTECTED_EMAIL
from core.decorators import strip_input
from core.utils import is_valid_email


class CreateUser(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        email = input["email"]
        password = input["password"]

        if not is_valid_email(email):
            raise ValidationError("The email is invalid!")
        elif email in PROTECTED_EMAIL:
            raise ValidationError("The email is being protected!")
        elif User.objects.filter(email=email).exists():
            raise ValidationError("The email is already in use!")

        user_service = UserService()
        result, user = user_service.create_user(
            email=email,
            password=password,
        )

        if result:
            return CreateUser(success=True, user=user)
        else:
            raise Exception("Can not create this user!")


class UserQuery(graphene.ObjectType):
    pass


class UserMutation(graphene.ObjectType):
    create_user = CreateUser.Field()
