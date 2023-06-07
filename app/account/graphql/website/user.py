from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from graphene import ResolveInfo
import graphene

from account.graphql.website.types.user import UserNode
from account.models import User
from account.services.user_service import UserService
from account.variables.protected_email import PROTECTED_EMAIL
from core.decorators import google_captcha3, strip_input
from core.utils import is_valid_email, is_valid_password


class CreateUser(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        captcha = graphene.String(
            required=settings.CAPTCHA["google_recaptcha3"]["enabled"]
        )

    success = graphene.Boolean()

    @classmethod
    @strip_input
    @google_captcha3("auth")
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
        if not is_valid_password(value=password, min_length=8):
            raise ValidationError("The password is invalid!")

        user_service = UserService()
        result, _ = user_service.create_user(
            email=email,
            password=password,
        )

        if result:
            return CreateUser(success=True)
        else:
            raise Exception("Can not create this user!")


class UserMutation(graphene.ObjectType):
    user_create = CreateUser.Field()


class UserQuery(graphene.ObjectType):
    user = graphene.relay.Node.Field(UserNode)
