from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from django_tenants.utils import schema_context
from graphene import ResolveInfo
from graphql_jwt.decorators import login_required
import graphene

from account.graphql.auth.types.user import UserNode
from account.models import User
from account.services.user_service import UserService
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
        captcha = graphene.String(
            required=settings.CAPTCHA["google_recaptcha3"]["enabled"]
        )

    success = graphene.Boolean()

    @classmethod
    @strip_input
    @google_captcha3("auth")
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
        captcha = graphene.String(
            required=settings.CAPTCHA["google_recaptcha3"]["enabled"]
        )

    success = graphene.Boolean()
    user = graphene.Field(UserNode)

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
        result, user = user_service.create_user(
            email=email,
            password=password,
        )

        if result:
            return CreateUser(success=True, user=user)
        else:
            raise Exception("Can not create this user!")


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

        user = info.context.user

        if not is_valid_email(email):
            raise ValidationError("The email is invalid!")
        elif email in PROTECTED_EMAIL:
            raise ValidationError("The email is being protected!")
        elif User.objects.filter(email=email).exclude(id=user.id).exists():
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


class UpdateName(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserNode)

    @classmethod
    @login_required
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        name = input["name"]

        user = info.context.user

        if User.objects.filter(name=name).exclude(id=user.id).exists():
            raise ValidationError("The email is already in use!")

        user.name = name
        user.save()

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
        name = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        old_email = input["oldEmail"]
        new_email = input["newEmail"]
        name = input["name"]
        password = input["password"]

        if not is_valid_email(old_email):
            raise ValidationError("The oldEmail is invalid!")
        elif not is_valid_email(new_email):
            raise ValidationError("The newEmail is invalid!")
        elif new_email in PROTECTED_EMAIL:
            raise ValidationError("The newEmail is being protected!")

        try:
            user = User.objects.get(email=old_email)
        except:
            raise Exception("Can not find this user!")
        else:
            if not user.check_password(password):
                raise ValidationError("The password is invalid!")
            elif User.objects.filter(email=new_email).exclude(id=user.id).exists():
                raise ValidationError("The newEmail is already in use!")

        if user.is_owner and old_email != new_email:
            user.email = new_email

        user.name = name
        user.save()

        if user.is_owner and user.email != old_email:
            with schema_context(settings.PUBLIC_SCHEMA_NAME):
                tenant_service = TenantService()
                tenant_service.updateEmail(
                    email_original=old_email,
                    email_new=new_email,
                )

        user.name = name
        user.save()

        return UpdateUser(success=True, user=user)


class UserQuery(graphene.ObjectType):
    pass


class UserMutation(graphene.ObjectType):
    check_name_available = CheckNameAvailable.Field()
    check_email_available = CheckEmailAvailable.Field()
    create_user = CreateUser.Field()
    update_email = UpdateEmail.Field()
    update_name = UpdateName.Field()
    update_password = UpdatePassword.Field()
    update_user = UpdateUser.Field()
