from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from django_tenants.utils import schema_context
from graphene import ResolveInfo
from graphql_jwt.decorators import login_required
import graphene

from account.graphql.auth.types.user import UserNode
from account.models import User
from account.variables.protected_email import PROTECTED_EMAIL
from core.decorators import google_captcha3, strip_input
from core.utils import is_valid_email, is_valid_password
from tenant.services.tenant_service import TenantService


class CheckEmailAvailable(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
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
        endpoint = info.context.headers.get("x-endpoint")

        if endpoint not in ("hq", "dashboard", "website"):
            raise Exception("Bad Request!")

        if not is_valid_email(email):
            raise ValidationError("The email is invalid!")
        elif email in PROTECTED_EMAIL:
            raise ValidationError("The email is being protected!")

        if info.context.user.is_authenticated:
            if (
                User.objects.filter(endpoint=endpoint, email=email)
                .exclude(id=info.context.user.id)
                .exists()
            ):
                raise ValidationError("The email is already in use!")
        else:
            if User.objects.filter(endpoint=endpoint, email=email).exists():
                raise ValidationError("The email is already in use!")

        return CheckEmailAvailable(success=True)


class CheckUsernameAvailable(graphene.relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        captcha = graphene.String(
            required=settings.CAPTCHA["google_recaptcha3"]["enabled"]
        )

    success = graphene.Boolean()

    @classmethod
    @strip_input
    @google_captcha3("auth")
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        username = input["username"]
        endpoint = info.context.headers.get("x-endpoint")

        if endpoint not in ("hq", "dashboard", "website"):
            raise Exception("Bad Request!")

        if info.context.user.is_authenticated:
            if (
                User.objects.filter(endpoint=endpoint, username=username)
                .exclude(id=info.context.user.id)
                .exists()
            ):
                raise ValidationError("The username is already in use!")
        else:
            if User.objects.filter(endpoint=endpoint, username=username).exists():
                raise ValidationError("The username is already in use!")

        return CheckUsernameAvailable(success=True)


class UpdateEmail(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserNode)

    @classmethod
    @login_required
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        email = input["email"]
        endpoint = info.context.headers.get("x-endpoint")

        if endpoint not in ("hq", "dashboard", "website"):
            raise Exception("Bad Request!")

        user = info.context.user

        if not is_valid_email(email):
            raise ValidationError("The email is invalid!")
        elif email in PROTECTED_EMAIL:
            raise ValidationError("The email is being protected!")
        elif (
            User.objects.filter(endpoint=endpoint, email=email)
            .exclude(id=user.id)
            .exists()
        ):
            raise ValidationError("The email is already in use!")

        email_original = user.email

        user.email = email
        user.save()

        if user.email != email_original:
            with schema_context(settings.PUBLIC_SCHEMA_NAME):
                tenant_service = TenantService()
                tenant_service.updateEmail(
                    email_original=email_original, email_new=user.email
                )

        return UpdateEmail(success=True, user=user)


class UpdatePassword(graphene.relay.ClientIDMutation):
    class Input:
        oldPassword = graphene.String(required=True)
        newPassword = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        old_password = input["oldPassword"]
        new_password = input["newPassword"]

        if not is_valid_password(value=new_password, min_length=8):
            raise ValidationError("The newPassword is invalid!")
        elif old_password == new_password:
            raise ValidationError(
                "The newPassword cannot be the same as the oldPassword!"
            )

        user = info.context.user

        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
        else:
            raise ValidationError("The oldPassword is invalid!")

        return UpdatePassword(success=True)


class UpdateUser(graphene.relay.ClientIDMutation):
    class Input:
        oldEmail = graphene.String(required=True)
        newEmail = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        old_email = input["oldEmail"]
        new_email = input["newEmail"]
        username = input["username"]
        password = input["password"]
        endpoint = info.context.headers.get("x-endpoint")

        if endpoint not in ("hq", "dashboard", "website"):
            raise Exception("Bad Request!")

        if not is_valid_email(old_email):
            raise ValidationError("The oldEmail is invalid!")
        elif not is_valid_email(new_email):
            raise ValidationError("The newEmail is invalid!")
        elif new_email in PROTECTED_EMAIL:
            raise ValidationError("The newEmail is being protected!")

        try:
            user = User.objects.get(endpoint=endpoint, email=old_email)
        except:
            raise Exception("Can not find this user!")
        else:
            if not user.check_password(password):
                raise ValidationError("The password is invalid!")
            elif (
                User.objects.filter(endpoint=endpoint, email=new_email)
                .exclude(id=user.id)
                .exists()
            ):
                raise ValidationError("The newEmail is already in use!")

        if user.is_owner and old_email != new_email:
            user.email = new_email

        user.username = username
        user.save()

        if user.is_owner and user.email != old_email:
            with schema_context(settings.PUBLIC_SCHEMA_NAME):
                tenant_service = TenantService()
                tenant_service.updateEmail(
                    email_original=old_email,
                    email_new=new_email,
                )

        user.username = username
        user.save()

        return UpdateUser(success=True, user=user)


class UpdateUsername(graphene.relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserNode)

    @classmethod
    @login_required
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        username = input["username"]
        endpoint = info.context.headers.get("x-endpoint")

        if endpoint not in ("hq", "dashboard", "website"):
            raise Exception("Bad Request!")

        user = info.context.user

        if (
            User.objects.filter(endpoint=endpoint, username=username)
            .exclude(id=user.id)
            .exists()
        ):
            raise ValidationError("The email is already in use!")

        user.username = username
        user.save()

        return UpdateEmail(success=True, user=user)


class UserMutation(graphene.ObjectType):
    email_available_check = CheckEmailAvailable.Field()
    email_update = UpdateEmail.Field()
    password_update = UpdatePassword.Field()
    user_update = UpdateUser.Field()
    username_available_check = CheckUsernameAvailable.Field()
    username_update = UpdateUsername.Field()


class UserQuery(graphene.ObjectType):
    pass
