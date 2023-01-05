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


class CheckEmailAvailable(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        email = input["email"]

        if not is_valid_email(email):
            raise ValidationError("The email is invalid!")
        elif email in PROTECTED_EMAIL:
            raise ValidationError("The email is being protected!")

        if info.context.user.is_authenticated:
            if (
                User.objects.filter(email=email)
                .exclude(id=info.context.user.id)
                .exists()
            ):
                raise ValidationError("The email is already in use!")
        else:
            if User.objects.filter(email=email).exists():
                raise ValidationError("The email is already in use!")

        return CheckEmailAvailable(success=True)


class CheckNameAvailable(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        name = input["name"]

        if info.context.user.is_authenticated:
            if User.objects.filter(name=name).exclude(id=info.context.user.id).exists():
                raise ValidationError("The name is already in use!")
        else:
            if User.objects.filter(name=name).exists():
                raise ValidationError("The name is already in use!")

        return CheckNameAvailable(success=True)


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
    check_name_available = CheckNameAvailable.Field()
    check_email_available = CheckEmailAvailable.Field()
    create_user = CreateUser.Field()
